#!/usr/bin/env python3
"""One-time move of the data folders from corpus-builder/ to data/.

    python move_data.py            # show what would move
    python move_data.py --apply    # move it

Moves corpus-builder/{corpus,chunks,questions,runs} to data/. Nothing is overwritten:
if a destination folder already has content, that folder is skipped and reported.
The one exception is the question template shipped in data/questions/: your own
questions.yaml replaces it, and the template is kept as questions.template.yaml.

Paths are relative inside the data (manifest, manual additions, chunks), so nothing
needs re-running after the move.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
OLD = REPO / "corpus-builder"
NEW = REPO / "data"
FOLDERS = ["corpus", "chunks", "questions", "runs"]


def is_empty(d: Path) -> bool:
    return not d.exists() or not any(d.iterdir())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="actually move (default: dry run)")
    args = ap.parse_args()
    plan, skipped = [], []
    for name in FOLDERS:
        src, dst = OLD / name, NEW / name
        if not src.exists() or is_empty(src):
            continue
        if name == "questions" and (dst / "questions.yaml").exists() and not (src / "questions.yaml").exists():
            skipped.append(f"{src}: no questions.yaml inside, nothing to move")
            continue
        if name == "questions" and dst.exists():
            others = [p for p in dst.iterdir() if p.name not in ("questions.yaml", "questions.template.yaml")]
            if others:
                skipped.append(f"{dst} has other files ({', '.join(p.name for p in others)}); move {src} by hand")
                continue
            plan.append((src, dst, "questions"))
        elif not is_empty(dst):
            skipped.append(f"{dst} already has content; leaving {src} where it is")
        else:
            plan.append((src, dst, "folder"))

    if not plan and not skipped:
        print("Nothing to move: corpus-builder/ has no data folders. You're on the new layout.")
        return 0
    for src, dst, kind in plan:
        print(f"{'Moving' if args.apply else 'Would move'} {src.relative_to(REPO)} -> {dst.relative_to(REPO)}")
        if not args.apply:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if kind == "questions":
            dst.mkdir(exist_ok=True)
            template = dst / "questions.yaml"
            if template.exists():
                template.replace(dst / "questions.template.yaml")
            for f in src.iterdir():
                shutil.move(str(f), str(dst / f.name))
            src.rmdir()
        else:
            if dst.exists():
                dst.rmdir()  # empty, checked above
            shutil.move(str(src), str(dst))
    for s in skipped:
        print(f"Skipped: {s}")
    if not args.apply and plan:
        print("\nDry run. Run again with --apply to move.")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
