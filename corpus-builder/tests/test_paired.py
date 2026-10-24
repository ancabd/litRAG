"""Paired comparison of runs, effort accounting, and compare output."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation.paired import paired_compare, paired_diff, sign_test  # noqa: E402
from evaluation.runner import compare_runs  # noqa: E402


def test_sign_test_exact_values():
    assert sign_test(5, 0) == pytest.approx(2 / 32)          # 5 of 5 better: p = 0.0625
    assert sign_test(8, 0) == pytest.approx(2 / 256)
    assert sign_test(3, 3) == 1.0 and sign_test(0, 0) == 1.0
    assert sign_test(9, 1) == pytest.approx(2 * 11 / 1024)   # P(X <= 1) * 2 with n = 10


def test_paired_diff_counts_and_interval():
    a = {f"q{i}": 0.0 for i in range(10)}
    b = {f"q{i}": 1.0 if i < 8 else 0.0 for i in range(10)}
    r = paired_diff(a, b, "correct")
    assert r["n"] == 10 and r["diff"] == pytest.approx(0.8) and (r["better"], r["worse"], r["tied"]) == (8, 0, 2)
    assert r["lo"] > 0 and r["clear"] and r["p"] < 0.01 and r["better_ids"] == [f"q{i}" for i in range(8)]


def test_paired_diff_skips_unscored_and_respects_lower_is_better():
    a = {"q1": 1.0, "q2": 0.0, "q3": None, "q4": 1.0}
    b = {"q1": 0.0, "q2": 0.0, "q3": 1.0}
    r = paired_diff(a, b, "invalid_citations")             # lower is better: B fixed q1
    assert r["n"] == 2 and r["better"] == 1 and r["worse"] == 0 and r["lower_is_better"]
    assert paired_diff({"q1": None}, {"q1": 1.0}) is None


def test_identical_runs_show_no_difference():
    a = {f"q{i}": float(i % 2) for i in range(12)}
    r = paired_diff(a, dict(a), "hit@5")
    assert r["diff"] == 0 and r["lo"] == 0 and r["hi"] == 0 and not r["clear"] and r["p"] == 1.0


def write_run(root: Path, name: str, values: dict[str, float], effort: dict | None = None) -> Path:
    d = root / name
    d.mkdir(parents=True)
    rows = [{"id": q, "question": q, "metrics": {"correct": v}} for q, v in values.items()]
    (d / "per_question.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    mean = sum(values.values()) / len(values)
    (d / "summary.json").write_text(json.dumps({
        "kind": "answer", "questions_sha1": "abc", "effort": effort,
        "results": {"all": {"correct": {"mean": mean, "lo": mean, "hi": mean, "n": len(values)}}}}))
    return d


def test_compare_runs_adds_paired_table_and_effort(tmp_path):
    base = write_run(tmp_path, "single", {f"q{i}": 0.0 for i in range(6)},
                     {"turns": 1.0, "searches": 1.0, "passages_read": 8.0, "input_tokens": 4000.0, "cost": 0.01, "seconds": 2.0})
    agent = write_run(tmp_path, "agent", {f"q{i}": 1.0 for i in range(6)},
                      {"turns": 3.0, "searches": 2.5, "passages_read": 14.0, "input_tokens": 15000.0, "cost": 0.004, "seconds": 7.0})
    out = compare_runs([base, agent], metrics=["correct"])
    assert "Paired, per question: **agent** minus **single**" in out
    assert "**+1.00 [+1.00, +1.00]**" in out and "6 / 0 / 0" in out and "0.031" in out
    assert "| turns | 1.0 | 3.0 |" in out and "$0.0040" in out
    assert paired_compare(base, agent, ["correct", "missing"]).keys() == {"correct"}
