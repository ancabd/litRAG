"""Answer a question from the corpus, with citations.

    lib = Library.load(paths.default_chunk_run())
    generator = get_generator("claude", model="claude-sonnet-5-5", cache_dir=paths.CACHE / "llm")
    ans = generator.answer("What test system ...?", lib, k=8)      # or answer_question(...)
    ans.answer, ans.citations, ans.answerable, ans.trace

A generator gets the question and the Library, and decides itself what to read. Single-shot
generators search once and answer from the top k passages; an agent can search, read and
search again. Either way the result is an Answer whose `passages` are every passage the
generator saw, and whose citations are checked against them.

Generators:
  claude      single shot: an LLM answers from the top k passages (needs ANTHROPIC_API_KEY)
  extractive  single shot, no LLM: the sentence of the top k passages that best overlaps the
              question. A floor for comparison, and a way to try the pipeline without a key.
  agent       Claude searches and reads with tools, in a loop, until it can answer (agent.py)

To add one: subclass Generator (or SingleShotGenerator), add it to GENERATORS and get_generator.
"""
from __future__ import annotations

import re
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from .llm import DEFAULT_MODEL, LLM, LLMResponse, make_llm, parse_json
from .prompts import ANSWER_SYSTEM, ANSWER_VERSION, answer_prompt

if TYPE_CHECKING:
    from library import Library

CHUNK_ID = re.compile(r"^[A-Za-z0-9]+#\d{3,}$")
BRACKETS = re.compile(r"\[([^\[\]]{3,200})\]")


def extract_citations(text: str) -> list[str]:
    """Chunk ids cited as [W1#002], [W1#002; W2#010] or [W1#002, W2#010], in order of first use."""
    out: list[str] = []
    for group in BRACKETS.findall(text or ""):
        for part in re.split(r"[;,\s]+", group):
            part = part.strip()
            if CHUNK_ID.match(part) and part not in out:
                out.append(part)
    return out


@dataclass
class Answer:
    question: str
    answer: str
    answerable: bool
    citations: list[str]                      # cited chunk ids that the generator had seen
    invalid_citations: list[str]              # cited ids it never saw (made up)
    passages: list[dict]                      # every passage it saw: [{chunk_id, rank, score, step}]
    generator: dict
    prompt_version: str | None = None
    input_tokens: int = 0                     # over all LLM calls, including prompt-cache reads
    output_tokens: int = 0
    cost: float | None = 0.0
    seconds: float = 0.0
    cached: bool = False
    raw: str | None = None
    warnings: list[str] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)  # one entry per step, see Trace
    cache_read_tokens: int = 0                # input tokens served from the provider's prompt cache

    def to_dict(self) -> dict:
        return asdict(self)


StepCallback = Callable[[dict], None]


class Trace:
    """What a generator did, step by step, and what it saw.

    Each step: {step, action, input, chunks, input_tokens, output_tokens, seconds, note?}
    `chunks` are the chunk ids the step returned. `on_step` is called after every step
    (for streaming progress to the UI).
    """

    def __init__(self, on_step: StepCallback | None = None):
        self.steps: list[dict] = []
        self.seen: dict[str, dict] = {}       # chunk_id -> {chunk_id, rank, score, step}, in order first seen
        self.responses: list[LLMResponse] = []
        self.on_step = on_step
        self.t0 = time.perf_counter()

    def add(self, action: str, input: dict, chunks: list[str] | None = None, response: LLMResponse | None = None,
            seconds: float | None = None, **extra) -> dict:
        if response is not None:
            self.responses.append(response)
        step = {"step": len(self.steps) + 1, "action": action, "input": input, "chunks": list(chunks or []),
                "input_tokens": response.input_tokens if response else 0,
                "output_tokens": response.output_tokens if response else 0,
                "cache_read_tokens": response.cache_read_tokens if response else 0,
                "seconds": round(seconds if seconds is not None else (response.seconds if response else 0.0), 3),
                **extra}
        self.steps.append(step)
        if self.on_step:
            self.on_step(step)
        return step

    def saw(self, hits, step: int | None = None) -> None:
        """Record retrieved hits (anything with chunk_id and score) as seen."""
        for h in hits:
            if h.chunk_id not in self.seen:
                self.seen[h.chunk_id] = {"chunk_id": h.chunk_id, "rank": len(self.seen) + 1,
                                         "score": round(float(h.score), 4), "step": step or len(self.steps) + 1}

    def saw_chunks(self, chunk_ids: list[str], step: int | None = None) -> None:
        """Record passages read without a score (e.g. neighbours of a passage)."""
        for cid in chunk_ids:
            if cid not in self.seen:
                self.seen[cid] = {"chunk_id": cid, "rank": len(self.seen) + 1, "score": None,
                                  "step": step or len(self.steps) + 1}


def finish_answer(question: str, text: str, answerable: bool, trace: Trace, generator: "Generator",
                  warnings: list[str] | None = None) -> Answer:
    """Build the Answer: check citations against everything seen, add up usage across all LLM calls."""
    warnings = list(warnings or [])
    seen = trace.seen
    cited = extract_citations(text)
    invalid = [c for c in cited if c not in seen]
    if invalid:
        warnings.append(f"cited {len(invalid)} passage id(s) that were not provided: {', '.join(invalid)}")
    if answerable and not cited:
        warnings.append("answer has no citations")
    rs = trace.responses
    costs = [r.cost for r in rs]
    return Answer(
        question=question, answer=text, answerable=answerable,
        citations=[c for c in cited if c in seen], invalid_citations=invalid,
        passages=list(seen.values()), generator=generator.config(), prompt_version=generator.prompt_version,
        input_tokens=sum(r.input_tokens for r in rs), output_tokens=sum(r.output_tokens for r in rs),
        cost=None if any(c is None for c in costs) else sum(costs),
        seconds=round(time.perf_counter() - trace.t0, 3), cached=bool(rs) and all(r.cached for r in rs),
        raw=rs[-1].text if rs else None, warnings=warnings, trace=trace.steps,
        cache_read_tokens=sum(r.cache_read_tokens for r in rs),
    )


class Generator(ABC):
    name = "base"
    prompt_version: str | None = None

    @abstractmethod
    def answer(self, question: str, library: "Library", k: int = 8, retriever: str = "bm25",
               on_step: StepCallback | None = None) -> Answer:
        """Answer `question` from `library`. `k` is the passages per search; `on_step` gets each trace step."""

    def config(self) -> dict:
        return {"name": self.name}


class SingleShotGenerator(Generator):
    """Search once with the question, then answer from the top k passages."""

    @abstractmethod
    def generate(self, question: str, passages: list[dict]) -> tuple[str, bool, LLMResponse | None, list[str]]:
        """-> (answer text, answerable, llm response or None, warnings)"""

    def answer(self, question, library, k=8, retriever="bm25", on_step=None):
        trace = Trace(on_step)
        t = time.perf_counter()
        hits = library.search(question, k=k, retriever=retriever)
        trace.saw(hits, step=1)
        trace.add("search", {"query": question, "k": k, "retriever": retriever}, [h.chunk_id for h in hits],
                  seconds=time.perf_counter() - t)
        passages = [library.chunk(h.chunk_id) for h in hits]
        text, answerable, r, warnings = self.generate(question, passages)
        trace.add("answer", {"passages": len(passages)}, response=r)
        return finish_answer(question, text, answerable, trace, self, warnings)


class LLMGenerator(SingleShotGenerator):
    name = "claude"
    prompt_version = ANSWER_VERSION

    def __init__(self, llm: LLM, max_tokens: int = 700):
        self.llm, self.max_tokens = llm, max_tokens

    def config(self) -> dict:
        return {"name": self.name, **self.llm.config(), "prompt": ANSWER_VERSION}

    def generate(self, question, passages):
        r = self.llm.complete(ANSWER_SYSTEM, answer_prompt(question, passages), self.max_tokens)
        data = parse_json(r.text)
        warnings = []
        if data is None or "answer" not in data:
            warnings.append("model did not return the expected JSON; using its raw text as the answer")
            text = r.text.strip()
            answerable = bool(text) and not re.search(r"\b(not|no)\b.{0,40}\b(contain|answer|mention)", text, re.I)
        else:
            text = str(data.get("answer") or "").strip()
            answerable = bool(data.get("answerable", True)) and bool(text)
        return text, answerable, r, warnings


class ExtractiveGenerator(SingleShotGenerator):
    """Baseline without an LLM: the passage sentence with the largest word overlap with the question."""

    name = "extractive"
    STOP = frozenset("a an and are as at be by for from how in is it of on or the to was what which who why with "
                     "does do did their this that these those its into than use used using".split())

    def __init__(self, min_overlap: int = 2):
        self.min_overlap = min_overlap

    def config(self) -> dict:
        return {"name": self.name, "min_overlap": self.min_overlap}

    def _words(self, s: str) -> set[str]:
        return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in self.STOP and len(w) > 1}

    def generate(self, question, passages):
        q = self._words(question)
        best, best_score = None, 0
        for p in passages:
            for sent in re.split(r"(?<=[.!?])\s+", p["text"]):
                score = len(q & self._words(sent))
                if score > best_score:
                    best, best_score = (sent.strip(), p["chunk_id"]), score
        if best is None or best_score < self.min_overlap:
            return "The retrieved passages don't answer this question.", False, None, []
        return f"{best[0]} [{best[1]}]", True, None, []


GENERATORS = {"claude": "single shot: Claude answers from the top k passages",
              "extractive": "single shot, no LLM: best-overlapping sentence (baseline)",
              "agent": "Claude searches and reads with tools until it can answer"}


def available_generators() -> list[str]:
    return sorted(GENERATORS)


def get_generator(name: str, model: str = DEFAULT_MODEL, cache_dir: Path | None = None,
                  api_key: str | None = None, llm: LLM | None = None, **options) -> Generator:
    """`options` go to the generator, e.g. max_turns=4 or tools=("search",) for the agent."""
    if name == "extractive":
        return ExtractiveGenerator(**options)
    if name == "claude":
        return LLMGenerator(llm or make_llm(model, cache_dir, api_key), **options)
    if name == "agent":
        from .agent import AgentGenerator
        return AgentGenerator(llm or make_llm(model, cache_dir, api_key), **options)
    raise ValueError(f"Unknown generator {name!r}. Available: {', '.join(available_generators())}")


def answer_question(question: str, library: "Library", generator: Generator, k: int = 8,
                    retriever: str = "bm25", on_step: StepCallback | None = None) -> Answer:
    """Shorthand for generator.answer(...)."""
    return generator.answer(question, library, k=k, retriever=retriever, on_step=on_step)
