#!/usr/bin/env python3
"""Generate one index.qmd per chapter from the manifest.

The intro paragraph is real (states scope, lists method count, points to
the decision tree), then a methods table, then a labs table. No
fabricated narrative.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "_data" / "manifest.json").read_text(encoding="utf-8"))

CHAPTER_TITLES = {
    "01-foundations": "Statistical Foundations",
    "02-descriptives": "Descriptive Statistics",
    "03-probability": "Probability Theory",
    "04-inferential": "Inferential Statistics",
    "05-power": "Sample Size & Power",
    "06-visualisation": "Data Visualisation",
    "07-regression": "Regression & Modelling",
    "08-multivariate": "Multivariate Methods",
    "09-timeseries": "Time-Series Analysis",
    "10-bayesian": "Bayesian Statistics",
    "11-survival": "Survival Analysis",
    "12-bioinformatics": "Bioinformatics",
    "13-ml": "Machine Learning",
    "14-clinical": "Clinical Biostatistics",
    "15-metaanalysis": "Meta-Analysis",
    "16-design": "Experimental Design",
}

# A short scope paragraph per chapter — concrete, derived from contents,
# not invented narrative. Each ends with a pointer back to the decision
# tree.
SCOPE = {
    "01-foundations": (
        "This chapter covers the prerequisites that every later chapter "
        "assumes: the scientific process, tidy data, the R/Quarto/`renv` "
        "toolchain, measurement quality, missingness, and reproducibility. "
        "If you have never built a project with `renv` or written a "
        "pre-registration, start here."
    ),
    "02-descriptives": (
        "Methods for summarising a dataset before any inference: Table 1 "
        "construction, numerical summaries, and visual exploratory data "
        "analysis. Most papers in biomedicine open with a Table 1 — this "
        "chapter covers what belongs in it and how to render it cleanly "
        "with `gtsummary`."
    ),
    "03-probability": (
        "The probability machinery the rest of the book leans on: Bayes' "
        "rule, common discrete and continuous distributions, the law of "
        "total probability, Q-Q diagnostics, and density estimation. The "
        "chapter is short on theory and long on R-side intuition."
    ),
    "04-inferential": (
        "Classical inference: the Central Limit Theorem, MLE, NHST and "
        "its philosophy, t-tests and proportions, goodness-of-fit, "
        "correlation, and the non-parametric counterparts. This is the "
        "largest chapter and the one most peer reviewers will read first."
    ),
    "05-power": (
        "Sample-size and power calculations for the designs covered in "
        "the rest of the book — t-tests, ANOVA, regression, survival, "
        "diagnostic accuracy, equivalence and non-inferiority, sequential "
        "designs. Each method page includes the exact `pwr` or simulation "
        "call."
    ),
    "06-visualisation": (
        "The `ggplot2` grammar, panelled and faceted layouts, statistical "
        "graphics for regression and survival, and visual diagnostics. "
        "Style choices are biased toward what reproduces in print and "
        "what survives a black-and-white photocopy."
    ),
    "07-regression": (
        "Linear models, GLMs, GAMs, non-linear least squares, the ANOVA "
        "family, ANCOVA, robust regression, residual diagnostics, "
        "calibration, and decision-curve analysis. The chapter treats "
        "regression as a single object viewed from different angles."
    ),
    "08-multivariate": (
        "Methods for high-dimensional data without an outcome variable: "
        "principal components, factor analysis, canonical correlation, "
        "linear discriminant analysis, hierarchical and partition "
        "clustering, UMAP, and t-SNE. Both the variance-explained and "
        "the visual-projection use cases are covered."
    ),
    "09-timeseries": (
        "Stationarity, ARIMA, exponential smoothing, state-space models, "
        "spectral analysis, and forecasting evaluation. Examples use "
        "biomedical signals — heart rate, glucose, EEG — rather than "
        "macroeconomic data."
    ),
    "10-bayesian": (
        "Posterior inference via `brms` and Stan: priors, hierarchical "
        "models, posterior predictive checks, leave-one-out cross-"
        "validation, and Bayes factors. The chapter is opinionated: it "
        "treats Bayesian inference as a default, not an alternative."
    ),
    "11-survival": (
        "Time-to-event methods: Kaplan-Meier, Cox regression, time-"
        "varying covariates, competing risks, multistate models, and "
        "survival-targeted machine learning. Censoring is treated as a "
        "first-class concept, not a footnote."
    ),
    "12-bioinformatics": (
        "RNA-seq differential expression, pathway and GO enrichment, "
        "and single-cell RNA-seq. The chapter assumes basic familiarity "
        "with `Bioconductor` and points back to the regression and "
        "ML chapters for the underlying machinery."
    ),
    "13-ml": (
        "Cross-validation, regularisation (ridge/LASSO/elastic net), "
        "trees and ensembles, neural networks via `torch`/`keras`, "
        "SHAP and other interpretability tools, and the `tidymodels` "
        "workflow. False-discovery and knockoff-based selection are "
        "treated alongside CV as competing answers to the same question."
    ),
    "14-clinical": (
        "Diagnostic test accuracy, agreement (Bland-Altman, kappa, ICC), "
        "biomarker development, prediction-model reporting under "
        "TRIPOD-AI, and fairness audits. The chapter sits at the "
        "intersection of ML and biostatistics for a reason: that is "
        "where most regulatory submissions live."
    ),
    "15-metaanalysis": (
        "Pairwise random- and fixed-effects meta-analysis, network "
        "meta-analysis, individual-patient-data meta-analysis, and "
        "PRISMA-aligned reporting. Heterogeneity is treated as the main "
        "result, not a nuisance."
    ),
    "16-design": (
        "Study design across the spectrum: observational designs and "
        "STROBE, randomised trials, missing-data mechanisms and "
        "multiple imputation, mixed-effects models, DAGs and confounding, "
        "propensity scores, the g-methods family (IV, DiD, RDD, HTE), "
        "compartmental models for outbreaks, and the pre-registration / "
        "SAP / replication-crisis literature."
    ),
}


def list_files(chapter: str, kind: str) -> list[dict]:
    return [
        e for e in MANIFEST["entries"]
        if e["chapter"] == chapter and e["kind"] == kind
    ]


def page_link(target: str, chapter: str) -> str:
    # target is "chapters/<chapter>/<file>.qmd" or
    # "chapters/<chapter>/labs/<file>.qmd"; index.qmd lives at
    # "chapters/<chapter>/index.qmd" so links are relative.
    rel = target.removeprefix(f"chapters/{chapter}/")
    return rel


def build(chapter: str) -> str:
    title = CHAPTER_TITLES[chapter]
    scope = SCOPE[chapter]
    methods = sorted(list_files(chapter, "method"), key=lambda e: e["title"].lower())
    labs = sorted(list_files(chapter, "lab"), key=lambda e: (e.get("course", 0), e.get("lab_num", 0)))
    n_methods = len(methods)
    n_labs = len(labs)
    chap_num = chapter.split("-", 1)[0]

    out = [
        "---",
        f"title: \"{chap_num}. {title}\"",
        "---",
        "",
        f"# {title} {{#sec-ch-{chapter}}}",
        "",
        scope,
        "",
        f"This chapter contains **{n_methods} method pages** and "
        f"**{n_labs} lab{'s' if n_labs != 1 else ''}**. If you are not "
        "sure which method to read, return to "
        "[Chapter 0](../../ch00-find-your-method.qmd) and follow the "
        "decision tree to the right node.",
        "",
        "## Method pages",
        "",
    ]
    if methods:
        out += ["| Method | Source slug |", "|---|---|"]
        for e in methods:
            link = page_link(e["target"], chapter)
            out.append(f"| [{e['title']}]({link}) | `{Path(e['source']).stem}` |")
    else:
        out.append("*(no method pages in this chapter)*")
    out.append("")

    if labs:
        out += [
            "## Labs",
            "",
            "| # | Lab | Course / week / session |",
            "|---|---|---|",
        ]
        for e in labs:
            link = page_link(e["target"], chapter)
            week = (e["lab_num"] - 1) // 5 + 1
            session = (e["lab_num"] - 1) % 5 + 1
            out.append(
                f"| C{e['course']}.{e['lab_num']} | "
                f"[{e['title']}]({link}) | "
                f"Course {e['course']}, week {week}, session {session} |"
            )
        out.append("")

    return "\n".join(out)


def main() -> None:
    for chapter in CHAPTER_TITLES:
        path = ROOT / "chapters" / chapter / "index.qmd"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build(chapter), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
