#!/usr/bin/env python3
"""Rewrite legacy `courseN_name/labs/lab_weekX_sessionY.qmd` links to the
new `chapters/<chapter>/labs/lab-<slug>.qmd` paths, using the manifest.

Idempotent: rewrites only links that match the legacy pattern.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "_data" / "manifest.json").read_text(encoding="utf-8"))

COURSE_DIRS = {
    1: "course1_foundations",
    2: "course2_regression",
    3: "course3_design_causal",
    4: "course4_ml_highdim",
}

# (course_dir, week, session) -> new target relative to repo root
mapping: dict[tuple[str, int, int], str] = {}
for e in MANIFEST["entries"]:
    if e["kind"] != "lab":
        continue
    cdir = COURSE_DIRS[e["course"]]
    week = (e["lab_num"] - 1) // 5 + 1
    session = (e["lab_num"] - 1) % 5 + 1
    mapping[(cdir, week, session)] = e["target"]

LINK_RE = re.compile(
    r"(?P<prefix>(?:\.\./)+)"
    r"(?P<cdir>course[1-4]_[a-z_]+)"
    r"/labs/lab_week(?P<w>\d+)_session(?P<s>\d+)\.qmd"
)


def repath(file: Path, new_target: str) -> str:
    """Compute relative path from `file` to `new_target` (repo-relative)."""
    file_dir = file.parent.relative_to(ROOT)
    target = Path(new_target)
    # number of '..' = depth of file_dir
    up = "../" * len(file_dir.parts)
    return up + str(target).replace("\\", "/")


def fix_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    n = 0

    def sub(m: re.Match) -> str:
        nonlocal n
        key = (m.group("cdir"), int(m.group("w")), int(m.group("s")))
        if key not in mapping:
            return m.group(0)
        n += 1
        return repath(path, mapping[key])

    new = LINK_RE.sub(sub, text)
    if new != text:
        path.write_text(new, encoding="utf-8")
    return n


def main() -> None:
    total = 0
    files = 0
    for qmd in ROOT.rglob("*.qmd"):
        if "docs" in qmd.parts or ".git" in qmd.parts:
            continue
        n = fix_file(qmd)
        if n:
            total += n
            files += 1
    print(f"rewrote {total} legacy lab links across {files} files")


if __name__ == "__main__":
    main()
