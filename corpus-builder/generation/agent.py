"""The agent: Claude decides what to search and read, in a loop, until it can answer.

    question
       |
       v
    +--------------------------------+   tool calls    +------------------------------+
    | Claude: system prompt, tools,  | --------------> | run each tool on the Library |
    | the question, everything so far| <-------------- | (search, read_around,        |
    +--------------------------------+  tool results   |  open_paper)                 |
       | a reply with no tool call (the answer),        +------------------------------+
       | or give_up
       v
    Answer (+ trace of every step, + every passage it read)

Each turn sends the whole conversation, so it grows; prompt caching makes the repeated part
cheap. The loop ends when Claude replies without calling a tool (that reply is the answer) or
calls `give_up`. Two budgets keep it bounded: `max_turns` (model calls) and `token_budget`
(input + output tokens over all turns). On the last allowed turn only `give_up` is offered,
with a note to answer now, so it always ends. Citations are checked against everything it
read, exactly as for single-shot answers.
"""
from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING

from .answer import Generator, Trace, finish_answer
from .llm import LLM, LLMResponse
from .prompts import AGENT_FINAL_TURN, AGENT_SYSTEM, AGENT_VERSION
from .tools import GIVE_UP_TOOL, TOOLS, ToolContext, ToolResult

if TYPE_CHECKING:
    from library import Library

DEFAULT_TOOLS = ("search", "read_around", "open_paper")


def looks_answerable(text: str) -> bool:
    """Is a plain-text reply an answer, rather than a refusal written as text instead of calling give_up?

    Only an uncited reply that says the papers don't cover it counts as a refusal; a partial
    answer ("SchNet's cutoff isn't given, but NequIP uses 4 A [W..#003]") cites passages and counts.
    """
    if not text:
        return False
    if re.search(r"\[[A-Za-z0-9]+#\d{3,}\]", text):
        return True
    return not re.search(r"\b(not|no|don't|doesn't|cannot|can't)\b.{0,40}\b(contain|answer|mention|say|find|cover)",
                         text, re.I)


class AgentGenerator(Generator):
    name = "agent"
    prompt_version = AGENT_VERSION

    def __init__(self, llm: LLM, max_turns: int = 8, token_budget: int = 100_000,
                 tools: tuple[str, ...] = DEFAULT_TOOLS, max_tokens: int = 1024, cache: bool = True):
        unknown = [t for t in tools if t not in TOOLS]
        if unknown:
            raise ValueError(f"Unknown tool(s) {unknown}. Available: {sorted(TOOLS)}")
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1")
        self.llm, self.max_turns, self.token_budget = llm, max_turns, token_budget
        self.tools, self.max_tokens, self.cache = tuple(tools), max_tokens, cache

    def config(self) -> dict:
        return {"name": self.name, **self.llm.config(), "prompt": AGENT_VERSION, "tools": list(self.tools),
                "max_turns": self.max_turns, "token_budget": self.token_budget}

    def answer(self, question: str, library: "Library", k: int = 8, retriever: str = "bm25", on_step=None):
        trace = Trace(on_step)
        ctx = ToolContext(library, retriever=retriever, k=k)
        all_tools = [TOOLS[n].spec(ctx) for n in self.tools] + [GIVE_UP_TOOL]
        messages: list[dict] = [{"role": "user", "content": f"Question: {question}"}]
        used, warnings = 0, []
        text, answerable = "", False

        for turn in range(1, self.max_turns + 1):
            last = turn == self.max_turns or used >= self.token_budget
            if last and turn > 1:
                _append_text(messages[-1], AGENT_FINAL_TURN)
                if used >= self.token_budget:
                    warnings.append(f"token budget ({self.token_budget:,}) reached after {turn - 1} turns")
            r = self.llm.chat(AGENT_SYSTEM, messages, [GIVE_UP_TOOL] if last else all_tools,
                              self.max_tokens, cache=self.cache)
            used += r.input_tokens + r.output_tokens
            messages.append(r.message())
            thought = r.text.strip()

            if not r.tool_calls:  # a reply without tool calls is the final answer
                text = thought
                answerable = looks_answerable(text)
                if not text:
                    warnings.append("the model ended without an answer")
                elif not answerable:
                    warnings.append("the reply reads like 'not in the papers' but give_up wasn't called; "
                                    "counted as declining")
                if r.stop_reason == "max_tokens":
                    warnings.append("the answer was cut off at the output token limit")
                trace.add("answer", {}, response=r)
                break

            give_up = next((c for c in r.tool_calls if c.name == "give_up"), None)
            if give_up is not None:
                text = str(give_up.input.get("reason") or "").strip() or "The papers don't answer this question."
                answerable = False
                trace.add("give_up", give_up.input, response=r, thought=thought)
                break

            results = []
            for i, call in enumerate(r.tool_calls):
                t0 = time.perf_counter()
                res = self._run(call.name, call.input, ctx)
                step = len(trace.steps) + 1
                for cid in res.chunks:
                    _see(trace, cid, res.scores.get(cid), step)
                trace.add(call.name, call.input, res.chunks, response=r if i == 0 else None,
                          seconds=(r.seconds if i == 0 else 0.0) + time.perf_counter() - t0,
                          note=res.note, thought=thought if i == 0 else "", error=res.is_error)
                block = {"type": "tool_result", "tool_use_id": call.id, "content": res.text}
                if res.is_error:
                    block["is_error"] = True
                results.append(block)
            messages.append({"role": "user", "content": results})
        else:  # the last turn offered only give_up, yet it called another tool
            text, answerable = "", False
            warnings.append("stopped without an answer: the budget ran out")

        return finish_answer(question, text, answerable, trace, self, warnings)

    def _run(self, name: str, args: dict, ctx: ToolContext) -> ToolResult:
        if name not in self.tools:
            return ToolResult(f"There is no tool called {name}.", is_error=True, note=f"unknown tool {name}")
        try:
            return TOOLS[name].run(ctx, args or {})
        except (TypeError, ValueError) as exc:  # bad arguments from the model: tell it, let it retry
            return ToolResult(f"Invalid arguments for {name}: {exc}", is_error=True, note="invalid arguments")


def _see(trace: Trace, chunk_id: str, score: float | None, step: int) -> None:
    if chunk_id not in trace.seen:
        trace.seen[chunk_id] = {"chunk_id": chunk_id, "rank": len(trace.seen) + 1,
                                "score": None if score is None else round(float(score), 4), "step": step}


def _append_text(message: dict, text: str) -> None:
    """Add a text block to a user message (after any tool results, as the API requires)."""
    if isinstance(message["content"], str):
        message["content"] = [{"type": "text", "text": message["content"]}]
    message["content"].append({"type": "text", "text": text})


def usage_line(responses: list[LLMResponse]) -> str:
    read = sum(r.cache_read_tokens for r in responses)
    total = sum(r.input_tokens for r in responses)
    return f"{total:,} input tokens ({read:,} from the prompt cache)" if read else f"{total:,} input tokens"


__all__ = ["AgentGenerator", "DEFAULT_TOOLS", "looks_answerable"]
