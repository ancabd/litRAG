"""Library (search filters, reading around passages, paper outlines) and the LLM tool-use layer."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generation.answer import ExtractiveGenerator, Trace, finish_answer  # noqa: E402
from generation.llm import AnthropicLLM, CachedLLM, LLMResponse, ScriptedLLM, ToolCall  # noqa: E402
from library import Library  # noqa: E402


def chunk(paper, i, text, section, year=2020, source="pdf"):
    return {"chunk_id": f"{paper}#{i:03d}", "paper_id": paper, "index": i, "text": text, "section": section,
            "title": f"Paper {paper}", "year": year, "authors": "A. Author", "source": source,
            "page_start": 1 if source == "pdf" else None, "page_end": None}


CHUNKS = [
    chunk("BP", 0, "Neural network potentials for silicon.", "Abstract", 2007, "abstract"),
    chunk("BP", 1, "Symmetry functions describe the atomic environment within a cutoff.", "2 Methods"),
    chunk("BP", 2, "Radial symmetry functions use a cosine cutoff function.", "2 Methods > 2.1 Symmetry functions"),
    chunk("BP", 3, "Energies agree with DFT for bulk silicon.", "3 Results"),
    chunk("NQ", 1, "Equivariant convolutions; the cutoff radius is 4 Angstrom.", "2 Methods", 2022),
    chunk("NQ", 0, "NequIP is an E(3)-equivariant neural network potential.", "Abstract", 2022, "abstract"),
]


def lib():
    return Library([dict(c) for c in CHUNKS], name="test")


def test_search_filters_keep_k_and_renumber():
    L = lib()
    all_hits = L.search("cutoff", k=10)
    assert {h.chunk_id for h in all_hits} >= {"BP#001", "BP#002", "NQ#001"}
    only_nq = L.search("cutoff", k=3, paper="NQ")
    assert [h.chunk_id for h in only_nq] == ["NQ#001"] and only_nq[0].rank == 1
    recent = L.search("cutoff", k=5, year_from=2021)
    assert all(L.chunk(h.chunk_id)["year"] >= 2021 for h in recent)
    rest = L.search("cutoff", k=5, exclude={"NQ#001"})
    assert "NQ#001" not in {h.chunk_id for h in rest} and [h.rank for h in rest] == list(range(1, len(rest) + 1))


def test_retriever_is_built_once():
    L = lib()
    assert L.retriever("bm25") is L.retriever("bm25")


def test_neighbours_follow_reading_order():
    L = lib()
    assert [c["chunk_id"] for c in L.neighbours("BP#002")] == ["BP#001", "BP#002", "BP#003"]
    assert [c["chunk_id"] for c in L.neighbours("BP#000", before=2, after=1)] == ["BP#000", "BP#001"]
    # chunks of NQ are listed out of order in the file but sorted by index
    assert [c["chunk_id"] for c in L.neighbours("NQ#000", after=1)] == ["NQ#000", "NQ#001"]
    assert L.neighbours("nope#000") == []


def test_paper_outline_and_sections():
    p = lib().paper("BP")
    assert p["title"] == "Paper BP" and p["year"] == 2007 and p["source"] == "pdf" and p["n_chunks"] == 4
    assert [s["section"] for s in p["sections"]] == ["Abstract", "2 Methods", "2 Methods > 2.1 Symmetry functions",
                                                     "3 Results"]
    L = lib()
    assert [c["chunk_id"] for c in L.section_chunks("BP", "2 Methods")] == ["BP#001", "BP#002"]
    assert [c["chunk_id"] for c in L.section_chunks("BP", "2 Methods", include_subsections=False)] == ["BP#001"]
    assert L.paper("missing") is None


def test_load_from_run_folder(tmp_path):
    run = tmp_path / "pymupdf_w400_o60"
    run.mkdir()
    (run / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in CHUNKS))
    (run / "run.json").write_text(json.dumps({"parser": "pymupdf@2"}))
    L = Library.load(run)
    assert L.name == "pymupdf_w400_o60" and L.info["parser"] == "pymupdf@2" and len(L) == 6
    assert Library.load(run / "chunks.jsonl").name == "pymupdf_w400_o60"


# ------------------------------------------------------------------ trace and answers

def test_single_shot_answer_has_a_trace():
    steps = []
    ans = ExtractiveGenerator().answer("Which cutoff function do radial symmetry functions use?", lib(), k=3,
                                       on_step=steps.append)
    assert [s["action"] for s in ans.trace] == ["search", "answer"] and steps == ans.trace
    assert ans.trace[0]["chunks"] == [p["chunk_id"] for p in ans.passages]
    assert all(p["step"] == 1 for p in ans.passages) and ans.citations == ["BP#002"]


def test_finish_answer_checks_citations_against_everything_seen():
    L = lib()
    t = Trace()
    t.saw(L.search("cutoff", k=1))
    t.add("search", {"query": "cutoff"}, ["NQ#001"])
    t.saw_chunks(["BP#001", "BP#002"])
    r1 = LLMResponse("", "claude-haiku-5-5", 1000, 100)
    r2 = LLMResponse("", "claude-haiku-5-5", 2000, 50, cached=True)
    t.add("read_around", {"chunk_id": "BP#002"}, ["BP#001", "BP#002"], response=r1)
    t.add("answer", {}, response=r2)
    gen = ExtractiveGenerator()
    ans = finish_answer("q", "Cosine [BP#002] and [NQ#001], not [BP#003].", True, t, gen)
    assert ans.citations == ["BP#002", "NQ#001"] and ans.invalid_citations == ["BP#003"]
    assert ans.input_tokens == 3000 and ans.output_tokens == 150 and not ans.cached
    assert abs(ans.cost - r1.cost) < 1e-12  # the cached call is free
    assert [p["score"] is None for p in ans.passages] == [False, True, True]


# ------------------------------------------------------------------ tool use

TOOLS = [{"name": "search", "description": "Search the corpus.",
          "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}]


def scripted_agent(system, messages, tools):
    last = messages[-1]["content"]
    if isinstance(last, str):
        return {"text": "Let me search.", "tool_calls": [{"name": "search", "input": {"query": "cutoff"}}]}
    return "The cutoff is 4 Angstrom [NQ#001]."


def test_scripted_chat_round_trip():
    llm = ScriptedLLM(chat_respond=scripted_agent)
    messages = [{"role": "user", "content": "What cutoff does NequIP use?"}]
    r = llm.chat("sys", messages, TOOLS)
    assert r.stop_reason == "tool_use" and r.tool_calls == [ToolCall(r.tool_calls[0].id, "search", {"query": "cutoff"})]
    assert r.message()["content"][0] == {"type": "text", "text": "Let me search."}
    messages += [r.message(), {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": r.tool_calls[0].id, "content": "[NQ#001] ..."}]}]
    final = llm.chat("sys", messages, TOOLS)
    assert final.stop_reason == "end_turn" and not final.tool_calls and "[NQ#001]" in final.text
    assert len(llm.chats) == 2


def test_cached_chat_restores_tool_calls(tmp_path):
    inner = ScriptedLLM(chat_respond=scripted_agent, model="claude-haiku-5-5")
    llm = CachedLLM(inner, tmp_path)
    messages = [{"role": "user", "content": "q"}]
    first = llm.chat("sys", messages, TOOLS)
    second = llm.chat("sys", messages, TOOLS)
    assert len(inner.chats) == 1 and second.cached and second.cost == 0.0
    assert second.tool_calls == first.tool_calls and isinstance(second.tool_calls[0], ToolCall)
    llm.chat("sys", messages, None)  # different tools: a different request
    assert len(inner.chats) == 2
    # complete() and chat() never share entries
    inner.respond = lambda s, p: "plain"
    assert llm.complete("sys", "q").text == "plain"


def test_anthropic_chat_converts_blocks(monkeypatch):
    sent = {}

    class Messages:
        def create(self, **kw):
            sent.update(kw)
            return SimpleNamespace(
                content=[SimpleNamespace(type="text", text="Searching."),
                         SimpleNamespace(type="tool_use", id="toolu_1", name="search", input={"query": "x"})],
                usage=SimpleNamespace(input_tokens=120, output_tokens=30), stop_reason="tool_use")

    llm = AnthropicLLM.__new__(AnthropicLLM)
    llm.model, llm.client = "claude-sonnet-5-5", SimpleNamespace(messages=Messages())
    llm._anthropic = SimpleNamespace(APIError=RuntimeError)
    r = llm.chat("sys", [{"role": "user", "content": "q"}], TOOLS, max_tokens=500)
    assert sent["tools"] == TOOLS and sent["max_tokens"] == 500 and sent["system"] == "sys"
    assert r.text == "Searching." and r.tool_calls == [ToolCall("toolu_1", "search", {"query": "x"})]
    assert r.content[1] == {"type": "tool_use", "id": "toolu_1", "name": "search", "input": {"query": "x"}}
    assert r.stop_reason == "tool_use" and r.input_tokens == 120
    sent.clear()
    llm.chat("sys", [{"role": "user", "content": "q"}])
    assert "tools" not in sent  # omitted when there are none
