"""The agent loop, with a scripted model that makes tool calls (no network)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluate import main as evaluate_main  # noqa: E402
from evaluation.answer_runner import run_answer_eval  # noqa: E402
from generation import answer as answer_module  # noqa: E402
from generation.agent import AgentGenerator  # noqa: E402
from generation.llm import CachedLLM, LLMResponse, ScriptedLLM, ToolCall  # noqa: E402
from generation.prompts import AGENT_FINAL_TURN, AGENT_VERSION  # noqa: E402
from library import Library  # noqa: E402


def chunk(paper, i, text, section, title, year=2020):
    return {"chunk_id": f"{paper}#{i:03d}", "paper_id": paper, "index": i, "text": text, "section": section,
            "title": title, "year": year, "authors": "A. Author", "source": "pdf", "page_start": i + 1,
            "page_end": i + 1}


CHUNKS = [
    chunk("NQ", 0, "NequIP is an E(3)-equivariant neural network interatomic potential.", "Abstract", "NequIP", 2022),
    chunk("NQ", 1, "Message passing uses a radial cutoff of 4 Angstrom for all molecules.", "2 Methods", "NequIP", 2022),
    chunk("NQ", 2, "Training on 1000 configurations reaches state-of-the-art force accuracy.", "3 Results", "NequIP", 2022),
    chunk("SN", 0, "SchNet uses continuous-filter convolutions on interatomic distances.", "Abstract", "SchNet", 2018),
    chunk("SN", 1, "SchNet applies a cosine cutoff at 5 Angstrom to the filters.", "2 Model", "SchNet", 2018),
]


def lib():
    return Library([dict(c) for c in CHUNKS], name="agent-test")


def tool_results(messages):
    """All tool_result blocks so far, in order."""
    return [b for m in messages if m["role"] == "user" and isinstance(m["content"], list)
            for b in m["content"] if b.get("type") == "tool_result"]


def multihop(system, messages, tools):
    """Search NequIP's cutoff, then SchNet's, then answer citing both."""
    done = tool_results(messages)
    if len(done) == 0:
        return {"text": "First NequIP's cutoff.", "tool_calls": [{"name": "search", "input": {"query": "NequIP radial cutoff", "k": 2}}]}
    if len(done) == 1:
        return {"text": "Now SchNet.", "tool_calls": [{"name": "search", "input": {"query": "SchNet cosine cutoff", "k": 3}}]}
    return "NequIP uses a 4 Angstrom cutoff [NQ#001], smaller than SchNet's 5 Angstrom [SN#001]."


def test_multihop_two_searches_then_answer():
    llm = ScriptedLLM(chat_respond=multihop, model="claude-sonnet-5-5")
    steps = []
    ans = AgentGenerator(llm).answer("How does NequIP's cutoff compare to SchNet's?", lib(), k=5, on_step=steps.append)
    assert ans.answerable and ans.citations == ["NQ#001", "SN#001"] and not ans.invalid_citations
    assert [s["action"] for s in ans.trace] == ["search", "search", "answer"] and steps == ans.trace
    assert ans.trace[0]["thought"] == "First NequIP's cutoff." and ans.trace[0]["input"]["k"] == 2
    assert {p["chunk_id"] for p in ans.passages} >= {"NQ#001", "SN#001"}
    assert all(p["step"] in (1, 2) for p in ans.passages)
    assert ans.prompt_version == AGENT_VERSION and ans.generator["name"] == "agent"
    assert ans.input_tokens > 0 and len(llm.chats) == 3
    # each tool result answers the matching tool call
    second = llm.chats[2]
    uses = [b["id"] for m in second if m["role"] == "assistant" for b in m["content"] if b["type"] == "tool_use"]
    assert [b["tool_use_id"] for b in tool_results(second)] == uses


def test_repeated_passages_are_not_resent_in_full():
    def respond(system, messages, tools):
        if len(tool_results(messages)) < 2:
            return {"tool_calls": [{"name": "search", "input": {"query": "cutoff Angstrom", "k": 3}}]}
        return "4 Angstrom [NQ#001]."

    llm = ScriptedLLM(chat_respond=respond)
    ans = AgentGenerator(llm).answer("q", lib())
    first, second = [r["content"] for r in tool_results(llm.chats[-1])]
    n = len(ans.trace[0]["chunks"])
    assert n >= 2 and "already shown above" not in first and second.count("already shown above") == n
    assert ans.trace[1]["note"] == f"{n} passages, 0 new" and len(second) < len(first)


def test_parallel_calls_open_paper_and_read_around():
    def respond(system, messages, tools):
        if not tool_results(messages):
            return {"tool_calls": [{"name": "open_paper", "input": {"paper_id": "NQ"}},
                                   {"name": "read_around", "input": {"chunk_id": "NQ#001", "before": 0, "after": 1}}]}
        return "Accurate forces [NQ#002]."

    llm = ScriptedLLM(chat_respond=respond)
    ans = AgentGenerator(llm).answer("q", lib())
    opened, around = [r["content"] for r in tool_results(llm.chats[-1])]
    assert "NequIP (2022)" in opened and "- 2 Methods (NQ#001, 1)" in opened and "Abstract:" in opened
    assert "[NQ#001]" in around and "[NQ#002]" in around and "[NQ#000]" not in around
    assert ans.citations == ["NQ#002"] and ans.trace[1]["input_tokens"] == 0  # tokens counted once per turn


def test_bad_tool_calls_are_errors_the_model_can_recover_from():
    def respond(system, messages, tools):
        n = len(tool_results(messages))
        calls = [[{"name": "read_around", "input": {"chunk_id": "XX#999"}}],
                 [{"name": "search", "input": {"query": "cutoff", "paper_id": "nope"}}],
                 [{"name": "delete_everything", "input": {}}],
                 [{"name": "search", "input": {"query": "cutoff", "k": "many"}}]]
        if n < len(calls):
            return {"tool_calls": calls[n]}
        return {"tool_calls": [{"name": "give_up", "input": {"reason": "Nothing found."}}]}

    llm = ScriptedLLM(chat_respond=respond)
    ans = AgentGenerator(llm).answer("q", lib())
    results = tool_results(llm.chats[-1])
    assert all(r.get("is_error") for r in results)
    assert "No passage with id XX#999" in results[0]["content"] and "There is no tool" in results[2]["content"]
    assert "Invalid arguments" in results[3]["content"]
    assert not ans.answerable and ans.answer == "Nothing found." and [s["error"] for s in ans.trace[:4]] == [True] * 4


def told_to_answer(messages):
    last = messages[-1]["content"]
    return isinstance(last, list) and any(AGENT_FINAL_TURN in (b.get("text") or str(b.get("content") or "")) for b in last)


def test_turn_budget_forces_an_answer_without_changing_the_tools():
    seen_tools = []

    def respond(system, messages, tools):
        seen_tools.append(json.dumps(tools))
        if told_to_answer(messages):
            return "4 Angstrom [NQ#001]."
        return {"tool_calls": [{"name": "search", "input": {"query": "cutoff"}}]}

    llm = ScriptedLLM(chat_respond=respond)
    ans = AgentGenerator(llm, max_turns=3).answer("q", lib())
    names = [t["name"] for t in json.loads(seen_tools[0])]
    assert names == ["search", "read_around", "open_paper", "give_up"]
    assert len(seen_tools) == 3 and len(set(seen_tools)) == 1  # identical tools on every turn (thinking signatures)
    assert llm.chats[-1][-1]["content"][-1] == {"type": "text", "text": AGENT_FINAL_TURN}
    assert ans.answerable and ans.citations == ["NQ#001"]


def test_tool_calls_after_the_budget_are_refused_once_then_it_stops():
    def stubborn(system, messages, tools):
        return {"tool_calls": [{"name": "search", "input": {"query": "cutoff"}}]}

    llm = ScriptedLLM(chat_respond=stubborn)
    ans = AgentGenerator(llm, max_turns=2).answer("q", lib())
    assert [s["action"] for s in ans.trace] == ["search", "refused", "refused"]
    refusal = [b for b in llm.chats[-1][-1]["content"] if b.get("type") == "tool_result"][0]
    assert refusal["is_error"] and "budget is used up" in refusal["content"]
    assert not ans.answerable and any("kept calling tools" in w for w in ans.warnings) and len(llm.chats) == 3

    def obedient_after_refusal(system, messages, tools):
        results = tool_results(messages)
        if results and "budget is used up" in results[-1]["content"]:
            return "4 Angstrom [NQ#001]."
        return {"tool_calls": [{"name": "search", "input": {"query": "cutoff"}}]}

    ans = AgentGenerator(ScriptedLLM(chat_respond=obedient_after_refusal), max_turns=2).answer("q", lib())
    assert ans.answerable and ans.citations == ["NQ#001"] and [s["action"] for s in ans.trace][-1] == "answer"


def test_token_budget_ends_early():
    def respond(system, messages, tools):
        if told_to_answer(messages):
            return {"tool_calls": [{"name": "give_up", "input": {"reason": "Out of budget."}}]}
        return {"tool_calls": [{"name": "search", "input": {"query": "cutoff"}}]}

    ans = AgentGenerator(ScriptedLLM(chat_respond=respond), max_turns=10, token_budget=1).answer("q", lib())
    assert [s["action"] for s in ans.trace] == ["search", "give_up"]
    assert any("token budget" in w for w in ans.warnings) and not ans.answerable


def test_thinking_blocks_are_sent_back_unchanged():
    """Models that think return signed thinking blocks; the next request must carry them as they were."""
    calls = []

    class ThinkingLLM(ScriptedLLM):
        def chat(self, system, messages, tools=None, max_tokens=1024, cache=False):
            calls.append((json.loads(json.dumps(messages)), json.dumps(tools)))
            if len(calls) == 1:
                content = [{"type": "thinking", "thinking": "Search first.", "signature": "sig-abc"},
                           {"type": "tool_use", "id": "toolu_1", "name": "search", "input": {"query": "cutoff"}}]
                return LLMResponse("", self.model, 100, 20, content=content,
                                   tool_calls=[ToolCall("toolu_1", "search", {"query": "cutoff"})], stop_reason="tool_use")
            return LLMResponse("4 Angstrom [NQ#001].", self.model, 200, 20,
                               content=[{"type": "text", "text": "4 Angstrom [NQ#001]."}], stop_reason="end_turn")

    ans = AgentGenerator(ThinkingLLM(), max_turns=4).answer("q", lib())
    second_messages, second_tools = calls[1]
    assert second_messages[1]["content"][0] == {"type": "thinking", "thinking": "Search first.", "signature": "sig-abc"}
    assert second_tools == calls[0][1] and ans.citations == ["NQ#001"]


def test_plain_text_ending_and_made_up_citation():
    llm = ScriptedLLM(chat_respond=lambda s, m, t: "It is 4 Angstrom [NQ#001].")
    ans = AgentGenerator(llm).answer("q", lib())
    # it never searched, so NQ#001 was never shown: the citation is invalid
    assert ans.answerable and ans.invalid_citations == ["NQ#001"] and ans.citations == []
    assert [s["action"] for s in ans.trace] == ["answer"]


def test_refusal_written_as_text_counts_as_declining():
    ans = AgentGenerator(ScriptedLLM(chat_respond=lambda s, m, t: "The papers do not mention RFdiffusion.")).answer("q", lib())
    assert not ans.answerable and any("give_up wasn't called" in w for w in ans.warnings)
    from generation.agent import looks_answerable
    assert looks_answerable("SchNet's cutoff isn't given, but NequIP uses 4 Angstrom [NQ#001].")


def test_tool_subset_and_unknown_tool():
    gen = AgentGenerator(ScriptedLLM(chat_respond=multihop), tools=("search",))
    assert gen.config()["tools"] == ["search"]
    with pytest.raises(ValueError, match="Unknown tool"):
        AgentGenerator(ScriptedLLM(chat_respond=multihop), tools=("search", "browse_web"))


def test_cached_rerun_is_free_and_identical(tmp_path):
    inner = ScriptedLLM(chat_respond=multihop, model="claude-haiku-5-5")
    gen = AgentGenerator(CachedLLM(inner, tmp_path))
    first = gen.answer("How does NequIP's cutoff compare to SchNet's?", lib())
    second = gen.answer("How does NequIP's cutoff compare to SchNet's?", lib())
    assert len(inner.chats) == 3 and second.cached and second.cost == 0.0
    assert second.answer == first.answer and [s["action"] for s in second.trace] == ["search", "search", "answer"]


def test_prompt_cache_reads_are_cheaper():
    full = LLMResponse("", "claude-sonnet-5-5", input_tokens=10_000, output_tokens=0)
    cached = LLMResponse("", "claude-sonnet-5-5", input_tokens=10_000, output_tokens=0, cache_read_tokens=9_000)
    written = LLMResponse("", "claude-sonnet-5-5", input_tokens=10_000, output_tokens=0, cache_write_tokens=10_000)
    assert full.cost == pytest.approx(0.02)
    assert cached.cost == pytest.approx((1_000 + 9_000 * 0.05) * 2 / 1e6)
    assert written.cost == pytest.approx(0.025)


# ------------------------------------------------------------------ through the eval and the CLI

def write_run(tmp_path):
    cdir = tmp_path / "chunks" / "test_run"
    cdir.mkdir(parents=True)
    (cdir / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in CHUNKS))
    q = tmp_path / "questions.yaml"
    q.write_text("""- id: q001
  question: How does NequIP's cutoff compare to SchNet's?
  type: comparison
  split: dev
  answer: NequIP 4 Angstrom, SchNet 5 Angstrom.
  evidence:
  - paper: NQ
    quote: Message passing uses a radial cutoff of 4 Angstrom for all molecules.
  - paper: SN
    quote: SchNet applies a cosine cutoff at 5 Angstrom to the filters.
""")
    return cdir, q


def test_answer_eval_scores_what_the_agent_read(tmp_path):
    cdir, q = write_run(tmp_path)
    gen = AgentGenerator(ScriptedLLM(chat_respond=multihop, model="claude-sonnet-5-5"))
    run_dir = run_answer_eval(q, cdir, gen, None, k=5, out_root=tmp_path / "runs", name="agent")
    row = json.loads((run_dir / "per_question.jsonl").read_text().splitlines()[0])
    assert row["metrics"]["retrieved_gold"] == 1.0 and row["metrics"]["cites_gold"] == 1.0
    assert [s["action"] for s in row["answer"]["trace"]] == ["search", "search", "answer"]
    assert {r["chunk_id"] for r in row["retrieved"]} == {p["chunk_id"] for p in row["answer"]["passages"]}
    summary = json.loads((run_dir / "summary.json").read_text())
    assert summary["generator"]["name"] == "agent" and summary["generator"]["max_turns"] == 8


def test_cli_ask_with_agent_prints_trace(tmp_path, monkeypatch, capsys):
    cdir, _ = write_run(tmp_path)
    monkeypatch.setattr(answer_module, "make_llm",
                        lambda model, cache_dir=None, api_key=None: ScriptedLLM(chat_respond=multihop, model=model))
    code = evaluate_main(["ask", "--generator", "agent", "--chunks", str(cdir), "--no-cache", "--max-turns", "4",
                          "How does NequIP's cutoff compare to SchNet's?"])
    out = capsys.readouterr()
    assert code == 0 and "[NQ#001]" in out.out and "Sources:" in out.out
    assert 'search      "NequIP radial cutoff"' in out.err and "| Now SchNet." in out.err and "answer" in out.err


def test_search_tool_states_the_runs_default_k():
    seen = {}

    def respond(system, messages, tools):
        seen.update({t["name"]: t for t in tools})
        return "done"

    AgentGenerator(ScriptedLLM(chat_respond=respond)).answer("q", lib(), k=8)
    assert seen["search"]["input_schema"]["properties"]["k"]["description"] == "Number of passages (default 8)."


def test_answer_eval_records_effort(tmp_path):
    cdir, q = write_run(tmp_path)
    gen = AgentGenerator(ScriptedLLM(chat_respond=multihop, model="claude-sonnet-5-5"))
    run_dir = run_answer_eval(q, cdir, gen, None, k=5, out_root=tmp_path / "runs", name="agent")
    row = json.loads((run_dir / "per_question.jsonl").read_text().splitlines()[0])
    e = row["effort"]
    assert (e["turns"], e["tool_calls"], e["searches"]) == (3, 2, 2) and e["passages_read"] >= 2
    assert not e["gave_up"] and not e["hit_budget"] and e["cost"] > 0
    summary = json.loads((run_dir / "summary.json").read_text())
    assert summary["effort"]["turns"] == 3 and summary["effort"]["total_cost"] > 0
    assert "## Effort per question" in (run_dir / "report.md").read_text()
    assert 'steps: search "NequIP radial cutoff"' in (run_dir / "report.md").read_text()
