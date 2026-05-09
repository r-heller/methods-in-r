# Methods in R

*A topic reference for biomedical research and peer review.*

A Quarto book by **R. Heller** that consolidates and re-organises content
from two of my MIT-licensed public repositories under a topic-based spine,
adds a *For Reviewers* section to every method page, and aggregates
copy-paste reporting templates tagged by **STROBE / CONSORT / TRIPOD-AI /
PRISMA / ARRIVE**.

The rendered book is at
<https://r-heller.github.io/methods-in-r/>.

## Sources consolidated

- [`CTTIR/courses`](https://github.com/CTTIR/courses) — 80 labs across
  four 4-week courses. Re-homed by topic.
- [`CTTIR/tutorials`](https://github.com/CTTIR/tutorials) — 569 method
  pages across 16 topic areas, each in a 9-section template; extended
  here with a 10th section, *For Reviewers*.

Both source repos are MIT, authored by R. Heller. Provenance is recorded
in `MIGRATION_LOG.md`.

## Sibling volume

This is the second book in the *…in R* series. The first is
[`r-heller/strategy-in-r`](https://github.com/r-heller/strategy-in-r)
*Strategy in R: Game Theory, Simulation, and Machine Intelligence*.
The two share branding, build conventions (Quarto book, `renv`, GitHub
Pages deploy), and an R-only worked-example style.

## Structure

```
chapters/
  01-foundations/  …  16-experimental-design/   # 16 topic chapters
ch00-find-your-method.qmd                       # decision tree
reporting/                                      # copy-paste templates
  strobe.qmd consort.qmd tripod-ai.qmd prisma.qmd arrive.qmd
appendices/                                     # workflow, glossary, errors, cheats
shared/                                         # data, R helpers
scripts/                                        # build_manifest.py, inject_crosslinks.py
```

## Build

```bash
git clone https://github.com/r-heller/methods-in-r
cd methods-in-r
R -e 'renv::restore()'
quarto render          # HTML to docs/, PDF as docs/Methods-in-R.pdf
```

## Licence

- Code: MIT (see `LICENSE`).
- Written content: CC-BY-SA 4.0 (see `LICENSE-CONTENT`), attribution to *R. Heller, Methods in R*.
