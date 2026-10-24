"""Answer a question from retrieved passages, with citations.

    generator = get_generator("claude", model="claude-sonnet-5-5", cache_dir=paths.CACHE / "llm")
    ans = answer_question("What test system ...?", retriever, chunks_by_id, generator, k=8)
    ans.answer, ans.citations, ans.answerable

Generators:
  claude      an LLM answers from the passages (needs ANTHROPIC_API_KEY)
  extractive  no LLM: returns the sentence of the retrieved passages that best overlaps the
              question. A floor for comparison, and a way to try the pipeline without a key.
"""
from __future__ import annotations

import re
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .llm import DEFAULT_MODEL, LLM, LLMResponse, make_llm, parse_json
from .prompts import ANSWER_SYSTEM, ANSWER_VERSION, answer_prompt

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
    citations: list[str]                      # cited chunk ids that were among the passages
    invalid_citations: list[str]              # cited ids that were NOT given (made up)
    passages: list[dict]                      # [{chunk_id, rank, score}] given to the generator
    generator: dict
    prompt_version: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float | None = 0.0
    seconds: float = 0.0
    cached: bool = False
    raw: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class Generator(ABC):
    name = "base"

    @abstractmethod
    def generate(self, question: str, passages: list[dict]) -> tuple[str, bool, LLMResponse | None, list[str]]:
        """-> (answer text, answerable, llm response or None, warnings)"""

    def config(self) -> dict:
        return {"name": self.name}

    prompt_version: str | None = None


class LLMGenerator(Generator):
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


class ExtractiveGenerator(Generator):
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


GENERATORS = {"claude": LLMGenerator, "extractive": ExtractiveGenerator}


def available_generators() -> list[str]:
    return sorted(GENERATORS)


def get_generator(name: str, model: str = DEFAULT_MODEL, cache_dir: Path | None = None,
                  api_key: str | None = None, llm: LLM | None = None) -> Generator:
    if name == "extractive":
        return ExtractiveGenerator()
    if name == "claude":
        return LLMGenerator(llm or make_llm(model, cache_dir, api_key))
    raise ValueError(f"Unknown generator {name!r}. Available: {', '.join(available_generators())}")


def answer_question(question: str, retriever, chunks_by_id: dict[str, dict], generator: Generator,
                    k: int = 8, hits=None) -> Answer:
    """Retrieve the top k passages (or use `hits`), generate an answer, validate its citations."""
    t0 = time.perf_counter()
    hits = hits if hits is not None else retriever.search(question, k=k)
    passages = [chunks_by_id[h.chunk_id] for h in hits[:k]]
    text, answerable, r, warnings = generator.generate(question, passages)
    given = {p["chunk_id"] for p in passages}
    cited = extract_citations(text)
    invalid = [c for c in cited if c not in given]
    if invalid:
        warnings.append(f"cited {len(invalid)} passage id(s) that were not provided: {', '.join(invalid)}")
    if answerable and not cited:
        warnings.append("answer has no citations")
    return Answer(
        question=question, answer=text, answerable=answerable,
        citations=[c for c in cited if c in given], invalid_citations=invalid,
        passages=[{"chunk_id": h.chunk_id, "rank": i, "score": round(h.score, 4)} for i, h in enumerate(hits[:k], 1)],
        generator=generator.config(), prompt_version=generator.prompt_version,
        input_tokens=r.input_tokens if r else 0, output_tokens=r.output_tokens if r else 0,
        cost=r.cost if r else 0.0, seconds=round(time.perf_counter() - t0, 3), cached=bool(r and r.cached),
        raw=r.text if r else None, warnings=warnings,
    )
