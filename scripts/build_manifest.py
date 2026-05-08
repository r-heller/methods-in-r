#!/usr/bin/env python3
"""Walk source repos and emit _data/manifest.json for methods-in-r.

Sources (siblings of this repo):
  ../courses     (CTTIR/courses)
  ../tutorials   (CTTIR/tutorials)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIBLINGS = ROOT.parent
COURSES = SIBLINGS / "courses"
TUTORIALS = SIBLINGS / "tutorials"
OUT = ROOT / "_data" / "manifest.json"

# tutorials category dir -> chapter dir under chapters/
CATEGORY_TO_CHAPTER = {
    "statistical-foundations": "01-foundations",
    "descriptive-statistics": "02-descriptives",
    "probability": "03-probability",
    "inference": "04-inferential",
    "sample-size": "05-power",
    "visualisation": "06-visualisation",
    "regression-modelling": "07-regression",
    "multivariate": "08-multivariate",
    "time-series": "09-timeseries",
    "bayesian": "10-bayesian",
    "survival-analysis": "11-survival",
    "bioinformatics": "12-bioinformatics",
    "machine-learning": "13-ml",
    "clinical-biostatistics": "14-clinical",
    "meta-analysis": "15-metaanalysis",
    "experimental-design": "16-design",
}

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

# Lab to chapter mapping. Format: (course, lab_num) -> chapter_dir or "REPORTING"
# Courses index labs 1..20 across week1..4 x session1..5.
LAB_MAP_RAW = {
    # 01 Foundations
    "01-foundations": [(1, 1), (1, 2), (1, 3), (1, 4)],
    # 02 Descriptives
    "02-descriptives": [(1, 6)],
    # 03 Probability
    "03-probability": [(1, 7), (1, 9), (1, 10)],
    # 04 Inferential
    "04-inferential": [(1, n) for n in (11, 12, 13, 14, 15, 16, 17, 18, 19)],
    # 05 Power
    "05-power": [(1, 20), (3, 5)],
    # 06 Visualisation
    "06-visualisation": [(1, 5)],
    # 07 Regression
    "07-regression": [(2, n) for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19)],
    # 08 Multivariate
    "08-multivariate": [(4, 3), (4, 4), (4, 5)],
    # 09 Timeseries
    "09-timeseries": [(3, 10)],
    # 10 Bayesian
    "10-bayesian": [(4, 11), (4, 12)],
    # 11 Survival
    "11-survival": [(2, 18), (3, 11), (3, 12), (4, 14), (4, 15)],
    # 12 Bioinformatics
    "12-bioinformatics": [(4, 16), (4, 17), (4, 18)],
    # 13 ML
    "13-ml": [(4, n) for n in (1, 2, 6, 7, 8, 9, 10, 19)],
    # 14 Clinical
    "14-clinical": [(1, 8), (2, 17), (4, 13), (4, 20)],
    # 15 Meta
    "15-metaanalysis": [(3, 16), (3, 17), (3, 18)],
    # 16 Design
    "16-design": [(3, n) for n in (1, 2, 3, 4, 6, 7, 8, 9, 13, 14, 15, 19, 20)],
    # Reporting templates
    "REPORTING": [(2, 20)],
}

COURSE_DIRS = {
    1: "course1_foundations",
    2: "course2_regression",
    3: "course3_design_causal",
    4: "course4_ml_highdim",
}


def lab_filename(num: int) -> str:
    week = (num - 1) // 5 + 1
    session = (num - 1) % 5 + 1
    return f"lab_week{week}_session{session}.qmd"


def read_yaml_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return ""
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.S | re.M)
    if not m:
        return ""
    fm = m.group(1)
    t = re.search(r'^title:\s*"?(.+?)"?\s*$', fm, re.M)
    return t.group(1).strip() if t else ""


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "untitled"


def main() -> None:
    entries: list[dict] = []

    # Tutorials → method pages
    tut_root = TUTORIALS / "tutorials"
    for cat_dir in sorted(tut_root.iterdir()):
        if not cat_dir.is_dir():
            continue
        chapter = CATEGORY_TO_CHAPTER.get(cat_dir.name)
        if chapter is None:
            continue
        for qmd in sorted(cat_dir.glob("*.qmd")):
            if qmd.name == "index.qmd":
                continue
            title = read_yaml_title(qmd) or qmd.stem.replace("-", " ").title()
            entries.append({
                "kind": "method",
                "source": str(qmd.relative_to(SIBLINGS)).replace("\\", "/"),
                "title": title,
                "chapter": chapter,
                "chapter_title": CHAPTER_TITLES[chapter],
                "target": f"chapters/{chapter}/{qmd.name}",
                "category": cat_dir.name,
            })

    # Labs
    for chapter, pairs in LAB_MAP_RAW.items():
        for course, num in pairs:
            cdir = COURSES / COURSE_DIRS[course] / "labs"
            src = cdir / lab_filename(num)
            if not src.exists():
                print(f"[warn] missing lab: {src}")
                continue
            title = read_yaml_title(src) or src.stem
            slug = slugify(title.split("—", 1)[-1].strip() or src.stem)
            target_dir = "reporting" if chapter == "REPORTING" else f"chapters/{chapter}/labs"
            entries.append({
                "kind": "lab",
                "source": str(src.relative_to(SIBLINGS)).replace("\\", "/"),
                "title": title,
                "chapter": chapter,
                "chapter_title": CHAPTER_TITLES.get(chapter, "Reporting Templates"),
                "target": f"{target_dir}/lab-{slug}.qmd",
                "course": course,
                "lab_num": num,
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"entries": entries}, indent=2), encoding="utf-8")

    # Summary
    by_chapter: dict[str, dict[str, int]] = {}
    for e in entries:
        c = e["chapter"]
        by_chapter.setdefault(c, {"method": 0, "lab": 0})
        by_chapter[c][e["kind"]] += 1
    print(f"Wrote {OUT.relative_to(ROOT)} with {len(entries)} entries")
    for c in sorted(by_chapter):
        m = by_chapter[c]
        print(f"  {c}: {m.get('method',0)} methods, {m.get('lab',0)} labs")


if __name__ == "__main__":
    main()
