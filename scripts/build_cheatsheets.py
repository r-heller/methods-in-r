#!/usr/bin/env python3
"""Aggregate the 16 source cheatsheets into appendices/E-cheatsheets.qmd.

Each cheatsheet becomes a level-3 section nested under a thematic
level-2 heading. YAML front matter is stripped; everything else is
preserved verbatim.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIBLINGS = ROOT.parent
SRC = SIBLINGS / "courses" / "cheatsheets"
OUT = ROOT / "appendices" / "E-cheatsheets.qmd"

THEME_TITLES = {
    "course1_foundations": "Foundations",
    "course2_regression": "Regression",
    "course3_design_causal": "Design & Causal Inference",
    "course4_ml_highdim": "Machine Learning & High-Dimensional Data",
}

PART_TITLES = {
    "course1_foundations": {
        "1": "Toolchain, tidy data, and `ggplot2`",
        "2": "Descriptive statistics, Bayes, and distributions",
        "3": "Sampling, estimation, and one-sample tests",
        "4": "Two-group comparisons, effect sizes, and power",
    },
    "course2_regression": {
        "1": "Linear regression and diagnostics",
        "2": "ANOVA, mixed models, and non-linear regression",
        "3": "Generalised linear models and prediction evaluation",
        "4": "Agreement, survival primer, and reporting",
    },
    "course3_design_causal": {
        "1": "Study designs and power",
        "2": "Missing data, mixed models, and longitudinal",
        "3": "Causal inference methods",
        "4": "Synthesis and pre-registration",
    },
    "course4_ml_highdim": {
        "1": "Cross-validation, regularisation, and unsupervised",
        "2": "Trees, boosting, and interpretability",
        "3": "Bayesian and survival ML",
        "4": "Omics, FDR, and TRIPOD-AI",
    },
}


def strip_fm(text: str) -> str:
    return re.sub(r"^---\s*\n.*?\n---\s*\n?", "", text, count=1, flags=re.S)


def detopic(body: str) -> str:
    # Rename per-week decision-rule headings to a generic form.
    return re.sub(r"^(#+\s*Decision rule)\s+for Week\s+\d+\s*$",
                  r"\1", body, flags=re.M)


def main() -> None:
    parts = [
        "---",
        "title: \"Cheatsheets\"",
        "toc: true",
        "---",
        "",
        "# Cheatsheets",
        "",
        "One-page topical summaries, aggregated here as a printable "
        "reference. Each is a self-contained reminder of the syntax, the "
        "assumptions, and the diagnostics that go with the methods it "
        "covers.",
        "",
    ]
    for theme in ["course1_foundations", "course2_regression",
                  "course3_design_causal", "course4_ml_highdim"]:
        cdir = SRC / theme
        if not cdir.exists():
            continue
        parts.append(f"## {THEME_TITLES[theme]}")
        parts.append("")
        for sheet in sorted(cdir.glob("cheat_week*.qmd")):
            wn = re.search(r"week(\d+)", sheet.stem).group(1)
            body = detopic(strip_fm(sheet.read_text(encoding="utf-8")).strip())
            part_title = PART_TITLES[theme][wn]
            parts.append(f"### {part_title}")
            parts.append("")
            parts.append(body)
            parts.append("")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
