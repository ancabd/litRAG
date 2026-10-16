"""Retrieval metrics per question, aggregation with bootstrap confidence intervals.

Per question (answerable, with at least one resolved evidence item):
  hit@k         1 if any gold chunk is in the top k
  recall@k      fraction of evidence items with a gold chunk in the top k
                (equals hit@k for single-evidence questions; matters for multi-hop)
  mrr           1 / rank of the first gold chunk (0 if not retrieved)
  ndcg@10       binary-relevance nDCG over the top 10
  paper_hit@k   1 if any evidence *paper* has a chunk in the top k (right paper, maybe wrong passage)

Each is computed twice: strict (only the original evidence) and lenient (alternatives accepted
too; reported as lenient_<metric>). Plus:
  judged@10     fraction of the top 10 that you have judged (original, alternative, or not relevant).
                Low values mean unjudged passages may still answer the question, so even lenient
                scores can undercount.
"""
from __future__ import annotations

import math
import random

from retrieval.base import Hit

from .matching import ResolvedEvidence


def question_metrics(hits: list[Hit], chunk_paper: dict[str, str], evidence: list[ResolvedEvidence],
                     ks: tuple[int, ...], lenient: bool = False) -> dict[str, float]:
    """Strict: only the original evidence counts. Lenient: alternatives count too.

    An evidence item takes part only if its original quote resolved; alternatives widen what
    satisfies that item, they don't add items.
    """
    resolved = [e for e in evidence if e.resolved]
    item_gold = [e.lenient_chunks if lenient else e.gold_chunks for e in resolved]
    all_gold = set().union(*item_gold) if item_gold else set()
    ranked = [h.chunk_id for h in hits]

    def first_rank(gold: set[str]) -> int | None:
        return next((i for i, cid in enumerate(ranked, 1) if cid in gold), None)

    item_ranks = [first_rank(g) for g in item_gold]
    any_rank = first_rank(all_gold)
    papers = {e.paper for e in evidence} | (set().union(*(e.alt_papers for e in evidence)) if lenient else set())
    paper_rank = next((i for i, cid in enumerate(ranked, 1) if chunk_paper.get(cid) in papers), None)

    m: dict[str, float] = {}
    for k in ks:
        m[f"hit@{k}"] = float(any_rank is not None and any_rank <= k)
        m[f"recall@{k}"] = sum(r is not None and r <= k for r in item_ranks) / len(item_ranks)
        m[f"paper_hit@{k}"] = float(paper_rank is not None and paper_rank <= k)
    m["mrr"] = 1.0 / any_rank if any_rank else 0.0
    dcg = sum(1 / math.log2(i + 1) for i, cid in enumerate(ranked[:10], 1) if cid in all_gold)
    idcg = sum(1 / math.log2(i + 1) for i in range(1, min(len(all_gold), 10) + 1))
    m["ndcg@10"] = dcg / idcg if idcg else 0.0
    return m


def bootstrap_ci(values: list[float], n_boot: int = 2000, alpha: float = 0.05,
                 seed: int = 0) -> tuple[float, float, float]:
    """Mean and percentile bootstrap CI over questions."""
    if not values:
        return (float("nan"),) * 3
    mean = sum(values) / len(values)
    if len(values) == 1:
        return mean, mean, mean
    rng = random.Random(seed)
    n = len(values)
    means = sorted(sum(rng.choice(values) for _ in range(n)) / n for _ in range(n_boot))
    lo = means[int(alpha / 2 * n_boot)]
    hi = means[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    return mean, lo, hi


def aggregate(rows: list[dict], metric_names: list[str]) -> dict[str, dict]:
    """rows: per-question dicts with 'metrics'. Returns {metric: {mean, lo, hi, n}}."""
    out = {}
    for name in metric_names:
        vals = [r["metrics"][name] for r in rows]
        mean, lo, hi = bootstrap_ci(vals)
        out[name] = {"mean": mean, "lo": lo, "hi": hi, "n": len(vals)}
    return out
