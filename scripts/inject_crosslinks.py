#!/usr/bin/env python3
"""Idempotent 'See also' injection at the bottom of method pages and labs.

Each method page gets a 'See also — labs in this chapter' block that
lists every lab in the same chapter. Each lab gets a 'See also — methods
in this chapter' block. Blocks are wrapped in a fence comment so re-runs
replace rather than duplicate.

Currently the lab→methods cross-list is the chapter index; a per-page
mapping would require a topical index that does not yet exist.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "_data" / "manifest.json").read_text(encoding="utf-8"))

OPEN = "<!-- BEGIN see-also (auto-injected) -->"
CLOSE = "<!-- END see-also -->"


def block_for_method(chapter: str, current_target: str) -> str:
    labs = sorted(
        [e for e in MANIFEST["entries"]
         if e["kind"] == "lab" and e["chapter"] == chapter],
        key=lambda e: (e.get("course", 0), e.get("lab_num", 0)),
    )
    if not labs:
        return ""
    items = []
    for e in labs:
        rel = Path(e["target"]).name
        items.append(f"- [{e['title']}](labs/{rel})")
    return (
        f"\n{OPEN}\n\n"
        "## See also — labs in this chapter\n\n"
        + "\n".join(items)
        + f"\n\n{CLOSE}\n"
    )


def block_for_lab(chapter: str) -> str:
    return (
        f"\n{OPEN}\n\n"
        "## See also — chapter index\n\n"
        f"- [Methods in this chapter](../index.qmd)\n"
        f"- [Find your method (Chapter 0)](../../../ch00-find-your-method.qmd)\n\n"
        f"{CLOSE}\n"
    )


def replace_or_append(text: str, block: str) -> str:
    if not block:
        return text
    pattern = re.compile(re.escape(OPEN) + r".*?" + re.escape(CLOSE) + r"\n?", re.S)
    if pattern.search(text):
        return pattern.sub(block.lstrip("\n"), text)
    return text.rstrip() + "\n" + block


def main() -> None:
    n = 0
    for e in MANIFEST["entries"]:
        path = ROOT / e["target"]
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if e["kind"] == "method":
            block = block_for_method(e["chapter"], e["target"])
        else:
            if e["chapter"] == "REPORTING":
                continue
            block = block_for_lab(e["chapter"])
        new = replace_or_append(text, block)
        if new != text:
            path.write_text(new, encoding="utf-8")
            n += 1
    print(f"updated {n} files with see-also blocks")


if __name__ == "__main__":
    main()
