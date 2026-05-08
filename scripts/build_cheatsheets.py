#!/usr/bin/env python3
"""Aggregate the 16 weekly cheatsheets from courses/ into appendices/E-cheatsheets.qmd.

Each weekly cheatsheet becomes a level-2 section. YAML front matter is
stripped; everything else is preserved verbatim.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIBLINGS = ROOT.parent
SRC = SIBLINGS / "courses" / "cheatsheets"
OUT = ROOT / "appendices" / "E-cheatsheets.qmd"

COURSE_TITLES = {
    "course1_foundations": "Course 1 — Foundations",
    "course2_regression": "Course 2 — Regression",
    "course3_design_causal": "Course 3 — Design & Causal Inference",
    "course4_ml_highdim": "Course 4 — Machine Learning & High-Dimensional Data",
}


def strip_fm(text: str) -> str:
    return re.sub(r"^---\s*\n.*?\n---\s*\n?", "", text, count=1, flags=re.S)


def main() -> None:
    parts = [
        "---",
        "title: \"Cheatsheets\"",
        "toc: true",
        "---",
        "",
        "# Cheatsheets",
        "",
        "Weekly one-page summaries from the original `CTTIR/courses` "
        "labs, aggregated here as a printable reference. Each is a "
        "self-contained reminder of the syntax, the assumptions, and the "
        "diagnostics that go with the methods covered that week.",
        "",
    ]
    for course in ["course1_foundations", "course2_regression", "course3_design_causal", "course4_ml_highdim"]:
        cdir = SRC / course
        if not cdir.exists():
            continue
        parts.append(f"## {COURSE_TITLES[course]}")
        parts.append("")
        for week in sorted(cdir.glob("cheat_week*.qmd")):
            wn = re.search(r"week(\d+)", week.stem).group(1)
            body = strip_fm(week.read_text(encoding="utf-8")).strip()
            parts.append(f"### Week {wn}")
            parts.append("")
            parts.append(body)
            parts.append("")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
