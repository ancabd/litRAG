"""LLM-as-judge for generated answers: correctness against the reference, and support by the cited passages.

Judges make mistakes, so their verdicts are only as good as their agreement with you:
`agreement()` compares judge verdicts with yours (from the app's "Your verdict" buttons).
"""
from __future__ import annotations

from collections import Counter

from generation.llm import LLM, parse_json
from generation.prompts import (CORRECTNESS_SYSTEM, JUDGE_VERSION, SUPPORT_SYSTEM, correctness_prompt,
                                support_prompt)

CORRECTNESS_SCORE = {"correct": 1.0, "partial": 0.5, "incorrect": 0.0}
SUPPORT_SCORE = {"supported": 1.0, "partial": 0.5, "unsupported": 0.0}


class Judge:
    def __init__(self, llm: LLM, max_tokens: int = 300):
        self.llm, self.max_tokens = llm, max_tokens
        self.input_tokens = self.output_tokens = 0
        self.cost = 0.0

    def config(self) -> dict:
        return {**self.llm.config(), "prompt": JUDGE_VERSION}

    def _ask(self, system: str, prompt: str, allowed: dict) -> dict:
        r = self.llm.complete(system, prompt, self.max_tokens)
        self.input_tokens += r.input_tokens
        self.output_tokens += r.output_tokens
        self.cost += r.cost or 0.0
        data = parse_json(r.text) or {}
        verdict = str(data.get("verdict", "")).strip().lower()
        if verdict not in allowed:
            return {"verdict": None, "score": None, "reason": f"judge returned no valid verdict: {r.text[:200]}"}
        return {"verdict": verdict, "score": allowed[verdict], "reason": str(data.get("reason", "")).strip()}

    def correctness(self, question: str, reference: str, answer: str) -> dict:
        return self._ask(CORRECTNESS_SYSTEM, correctness_prompt(question, reference, answer), CORRECTNESS_SCORE)

    def support(self, answer: str, cited: list[dict]) -> dict:
        if not cited:
            return {"verdict": "unsupported", "score": 0.0, "reason": "no passages cited"}
        return self._ask(SUPPORT_SYSTEM, support_prompt(answer, cited), SUPPORT_SCORE)


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def agreement(rows: list[dict], human: dict[str, dict]) -> dict:
    """Judge vs your correctness verdicts on the questions you've checked."""
    pairs = [(r["judgments"]["correctness"]["verdict"], human[r["id"]]["correctness"])
             for r in rows
             if r["id"] in human and human[r["id"]].get("correctness")
             and (r.get("judgments") or {}).get("correctness", {}).get("verdict")]
    if not pairs:
        return {"n": 0, "agreement": None, "kappa": None, "disagreements": []}
    judge, you = [p[0] for p in pairs], [p[1] for p in pairs]
    return {
        "n": len(pairs),
        "agreement": sum(x == y for x, y in pairs) / len(pairs),
        "kappa": cohen_kappa(judge, you),
        "disagreements": [r["id"] for r in rows if r["id"] in human and human[r["id"]].get("correctness")
                          and (r.get("judgments") or {}).get("correctness", {}).get("verdict")
                          not in (None, human[r["id"]]["correctness"])],
    }
