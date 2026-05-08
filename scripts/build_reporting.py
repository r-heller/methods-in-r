#!/usr/bin/env python3
"""Build reporting/ skeletons: one subsection per method that maps to a
reporting guideline. Skeletons only — no fabricated prose.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "_data" / "manifest.json").read_text(encoding="utf-8"))

# Map source category → relevant reporting guideline(s)
CATEGORY_TO_GUIDELINES = {
    "experimental-design": ["strobe", "consort"],
    "clinical-biostatistics": ["tripod-ai", "consort"],
    "machine-learning": ["tripod-ai"],
    "meta-analysis": ["prisma"],
    "survival-analysis": ["strobe", "tripod-ai"],
    "regression-modelling": ["strobe", "tripod-ai"],
    "inference": ["strobe", "consort"],
    "sample-size": ["consort", "strobe"],
    "bioinformatics": ["arrive"],
}

GUIDELINE_TITLES = {
    "strobe": "STROBE — observational studies",
    "consort": "CONSORT — randomised trials",
    "tripod-ai": "TRIPOD-AI — prediction models",
    "prisma": "PRISMA — systematic reviews & meta-analyses",
    "arrive": "ARRIVE — animal research",
}

GUIDELINE_INTRO = {
    "strobe": (
        "STROBE — *Strengthening the Reporting of Observational Studies "
        "in Epidemiology* — covers cohort, case-control, and "
        "cross-sectional studies. The 22-item checklist is at "
        "<https://www.strobe-statement.org/>. The templates below cover "
        "the analytic methods you are most likely to use in a STROBE-"
        "aligned paper."
    ),
    "consort": (
        "CONSORT — *Consolidated Standards of Reporting Trials* — covers "
        "randomised controlled trials. The 25-item checklist and flow "
        "diagram are at <https://www.consort-statement.org/>. The "
        "templates below cover the analytic methods most often used "
        "for primary and secondary endpoints in a trial."
    ),
    "tripod-ai": (
        "TRIPOD-AI — *Transparent Reporting of a multivariable prediction "
        "model for Individual Prognosis Or Diagnosis, AI extension* — "
        "covers prediction models, including those built with machine "
        "learning. The checklist is at <https://www.tripod-statement.org/>. "
        "The templates below cover model development, validation, "
        "calibration, and fairness reporting."
    ),
    "prisma": (
        "PRISMA — *Preferred Reporting Items for Systematic reviews and "
        "Meta-Analyses* — covers systematic reviews and meta-analyses. "
        "The 27-item checklist and flow diagram are at "
        "<https://www.prisma-statement.org/>. The templates below cover "
        "pairwise and network meta-analysis methods."
    ),
    "arrive": (
        "ARRIVE — *Animal Research: Reporting of In Vivo Experiments* — "
        "covers preclinical animal research. The 21-item checklist is at "
        "<https://arriveguidelines.org/>. The templates below cover the "
        "statistical analyses most commonly required."
    ),
}


def method_section(e: dict) -> str:
    method_target = e["target"]  # chapters/<chapter>/<file>.qmd
    chapter = e["chapter"]
    file_anchor = Path(method_target).stem
    return (
        f"### {e['title']}\n\n"
        "**Methods paragraph (copy-paste, fill in italics):**\n\n"
        f"> *[N=]* participants/observations were analysed using "
        f"**{e['title']}** as implemented in *[package vX.Y]* in R "
        "*[vX.Y]*. Assumptions were checked: *[list checks performed]*. "
        "*[Effect size with 95% confidence interval reported as the "
        "primary outcome]*. Two-sided p-values use *α = 0.05*; "
        "*[multiple-comparison adjustment if any]*.\n\n"
        "**Results paragraph (copy-paste):**\n\n"
        f"> {e['title']} yielded *[estimate]* (95% CI *[lower, upper]*, "
        "p = *[value]*). *[Diagnostic / assumption summary]*. "
        "*[Sensitivity analysis result]*.\n\n"
        f"**Reviewer checklist for this method.** "
        f"→ [`{file_anchor}` — For Reviewers]"
        f"(../{method_target}#for-reviewers)\n\n"
        "<!-- TODO:reporting-template -->\n"
    )


def build_guideline(slug: str, methods: list[dict]) -> str:
    out = [
        "---",
        f"title: \"{GUIDELINE_TITLES[slug]}\"",
        "---",
        "",
        f"# {GUIDELINE_TITLES[slug]}",
        "",
        GUIDELINE_INTRO[slug],
        "",
        f"This page contains **{len(methods)} method-specific templates**. "
        "Each is a skeleton with placeholders in italics; the prose is "
        "written so you can paste it into a manuscript and replace only "
        "the bracketed values.",
        "",
    ]
    methods_sorted = sorted(methods, key=lambda e: e["title"].lower())
    for e in methods_sorted:
        out.append(method_section(e))
    return "\n".join(out)


def main() -> None:
    by_guideline: dict[str, list[dict]] = {g: [] for g in GUIDELINE_TITLES}
    for e in MANIFEST["entries"]:
        if e["kind"] != "method":
            continue
        cat = e.get("category", "")
        for g in CATEGORY_TO_GUIDELINES.get(cat, []):
            by_guideline[g].append(e)

    out_dir = ROOT / "reporting"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Index
    index = [
        "---",
        "title: \"Reporting Templates\"",
        "---",
        "",
        "# Reporting Templates",
        "",
        "Copy-paste Methods + Results paragraphs, organised by reporting "
        "guideline. Pages here are deliberately formulaic: fill the "
        "bracketed *italics* with your numbers, replace the placeholder "
        "package versions with what you actually used, and check the "
        "**Reviewer checklist** link for each method to confirm you have "
        "reported every diagnostic a reviewer expects to see.",
        "",
        "Templates are organised by guideline:",
        "",
    ]
    for slug, title in GUIDELINE_TITLES.items():
        n = len(by_guideline[slug])
        index.append(f"- **[{title}]({slug}.qmd)** — {n} method templates")
    index.append("")
    index.append(
        "Every page is currently a **skeleton**: placeholders, no "
        "narrative text. The prose is written by hand into the slots "
        "marked `<!-- TODO:reporting-template -->`."
    )
    (out_dir / "index.qmd").write_text("\n".join(index) + "\n", encoding="utf-8")

    for slug, methods in by_guideline.items():
        path = out_dir / f"{slug}.qmd"
        path.write_text(build_guideline(slug, methods), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} with {len(methods)} entries")


if __name__ == "__main__":
    main()
