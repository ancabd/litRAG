"""Paired comparison of two runs on the same questions.

Two runs' confidence intervals, computed separately, overlap for almost any difference you'll
see with 20-60 questions. But both runs answered the *same* questions, and most of the
question-to-question variation (some questions are just hard) is shared. Comparing per
question removes it:

  diff        mean over questions of (B - A), with a paired bootstrap 95% interval
              (resample questions, keep each question's pair together)
  better      questions where B scored higher than A (for "lower is better" metrics: lower)
  worse       questions where B scored worse
  p           two-sided exact sign test on better vs worse (ties dropped): how likely a split
              at least this lopsided is if neither run is really better. For 0/1 metrics this
              is the exact McNemar test.

Read `diff` and its interval first; p is a sanity check. Comparing many metrics or many runs
means some p < 0.05 by chance (about 1 in 20 comparisons when nothing differs).
"""
from __future__ import annotations

import json
import random
from math import comb
from pathlib import Path

# metrics where a lower value is better; everything else is higher-is-better
LOWER_IS_BETTER = {"invalid_citations", "abstained_when_answerable"}


def sign_test(better: int, worse: int) -> float:
    """Two-sided exact binomial (sign) test p-value, ties excluded."""
    n = better + worse
    if n == 0:
        return 1.0
    k = min(better, worse)
    tail = sum(comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired_diff(a: dict[str, float | None], b: dict[str, float | None], metric: str = "",
                n_boot: int = 2000, alpha: float = 0.05, seed: int = 0) -> dict | None:
    """Compare per-question values of one metric. Only questions scored in both runs count."""
    ids = sorted(q for q in set(a) & set(b) if a[q] is not None and b[q] is not None)
    if not ids:
        return None
    sign = -1.0 if metric in LOWER_IS_BETTER else 1.0
    d = [b[q] - a[q] for q in ids]
    better = [q for q, x in zip(ids, d) if sign * x > 0]
    worse = [q for q, x in zip(ids, d) if sign * x < 0]
    n = len(d)
    mean = sum(d) / n
    if n > 1:
        rng = random.Random(seed)
        means = sorted(sum(rng.choice(d) for _ in range(n)) / n for _ in range(n_boot))
        lo, hi = means[int(alpha / 2 * n_boot)], means[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    else:
        lo = hi = mean
    return {
        "n": n,
        "mean_a": sum(a[q] for q in ids) / n,
        "mean_b": sum(b[q] for q in ids) / n,
        "diff": mean, "lo": lo, "hi": hi,
        "better": len(better), "worse": len(worse), "tied": n - len(better) - len(worse),
        "better_ids": better, "worse_ids": worse,
        "p": sign_test(len(better), len(worse)),
        "lower_is_better": metric in LOWER_IS_BETTER,
        # the interval excludes 0: B differs from A beyond what resampling questions explains
        "clear": n > 1 and (lo > 0 or hi < 0),
    }


def load_metrics(run_dir: Path) -> dict[str, dict[str, float | None]]:
    """{question id: {metric: value}} from a run's per_question.jsonl."""
    out = {}
    path = Path(run_dir) / "per_question.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                out[r["id"]] = r.get("metrics") or {}
    return out


def paired_compare(base: Path, other: Path, metrics: list[str]) -> dict[str, dict]:
    """{metric: paired_diff(base -> other)} for every metric both runs have."""
    a, b = load_metrics(base), load_metrics(other)
    out = {}
    for m in metrics:
        res = paired_diff({q: v.get(m) for q, v in a.items()}, {q: v.get(m) for q, v in b.items()}, m)
        if res is not None:
            out[m] = res
    return out


def format_paired(name_a: str, name_b: str, res: dict[str, dict]) -> str:
    """Markdown table of paired differences."""
    lines = [f"Paired, per question: **{name_b}** minus **{name_a}**", "",
             "| metric | n | A | B | B - A [95% CI] | better / worse / tied | sign test p |", "|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        lib = " (lower is better)" if r["lower_is_better"] else ""
        cell = f"{r['diff']:+.2f} [{r['lo']:+.2f}, {r['hi']:+.2f}]"
        if r["clear"]:
            cell = f"**{cell}**"
        lines.append(f"| {m}{lib} | {r['n']} | {r['mean_a']:.2f} | {r['mean_b']:.2f} | {cell} | "
                     f"{r['better']} / {r['worse']} / {r['tied']} | {r['p']:.3f} |")
    lines += ["", "Bold: the interval excludes 0. 'better' already accounts for metrics where lower is better."]
    return "\n".join(lines)


__all__ = ["LOWER_IS_BETTER", "format_paired", "load_metrics", "paired_compare", "paired_diff", "sign_test"]
