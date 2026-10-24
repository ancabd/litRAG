"""Answering questions from the corpus (the Ask page), and the generator/judge setup shared with answer evals."""
from __future__ import annotations

import os
from pathlib import Path

from ..core import DEFAULT_MODEL, PRICES, LLMNotConfigured, available_generators, get_generator
from .chunks import RunData
from .evidence import chunk_view


class AnsweringService:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir / "llm"

    def status(self) -> dict:
        return {
            "configured": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "generators": available_generators(),
            "default_model": DEFAULT_MODEL,
            "models": list(PRICES),
            "prices": {m: {"input": p[0], "output": p[1]} for m, p in PRICES.items()},
        }

    def generator(self, name: str, model: str | None):
        """Raises LLMNotConfigured when the API key is missing."""
        return get_generator(name, model=model or DEFAULT_MODEL, cache_dir=self.cache_dir)

    def judge(self, model: str | None):
        from ..core import Judge, make_llm
        if not model or model == "none":
            return None
        return Judge(make_llm(model, self.cache_dir))

    def ask(self, run: RunData, question: str, retriever: str, generator: str, model: str | None, k: int,
            titles: dict[str, str]) -> dict:
        gen = self.generator(generator, model)
        ans = gen.answer(question, run, k=k, retriever=retriever)
        cited = {cid: i for i, cid in enumerate(ans.citations, 1)}
        passages = []
        for p in ans.passages:
            c = run.by_id[p["chunk_id"]]
            passages.append({**chunk_view(c), "rank": p["rank"], "score": p["score"],
                             "title": c.get("title") or titles.get(c["paper_id"]), "year": c.get("year"),
                             "authors": c.get("authors"), "cited_as": cited.get(p["chunk_id"])})
        return {**ans.to_dict(), "run": run.name, "retriever": retriever, "passages": passages}


__all__ = ["AnsweringService", "LLMNotConfigured"]
