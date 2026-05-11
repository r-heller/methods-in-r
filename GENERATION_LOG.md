# Generation Log

Append-only audit trail of significant build/repo changes.

## 2026-05-11 — Quarto → bookdown migration + v1.0.0 publish

- Audited structure of the Quarto book (680 `.qmd` files across 16 topic
  chapters + appendices + reporting + labs).
- Installed bookdown 0.46, rmarkdown 2.31, knitr 1.51, sessioninfo 1.2.3,
  tinytex 0.59, bslib 0.10.0, downlit 0.4.5, xml2 1.5.2, htmltools 0.5.9.
- Scaffolded bookdown config (`_bookdown.yml`, `_output.yml`,
  `_common.R`, `style/*`, `scripts/*`) per CLAUDE.md §A1–A6, §B2.
- Converted all 680 `.qmd` → `.Rmd` with batch transforms:
  cross-refs `@sec-/fig-/tbl-` → `\@ref(...)`, `{.unnumbered}` → `{-}`,
  `::: {.callout-X}` fences → `<div class="callout callout-X">`,
  `.qmd` link targets → `.Rmd`, broken Quarto hashpipe code fences
  normalised to ```` ```r ```` blocks.
- Added formal front/back matter: `00-impressum.Rmd`,
  `00-acknowledgments.Rmd`, `95-colophon.Rmd`, `99-references.Rmd`.
- Added PART separator files: `_part-foundations.Rmd`,
  `_part-modelling.Rmd`, `_part-applications.Rmd`,
  `_part-reporting-templates.Rmd`.
- Replaced CI: removed `deploy-pages.yml` (Quarto) and `render-pdf.yml`,
  added `.github/workflows/render-book.yml` (bookdown build +
  `gh-pages` deploy) and `.github/workflows/citation-check.yml`.
- README: stripped marketing tone, added downloads and BibTeX block,
  no shields/badges.
- Added `CITATION.cff` (CFF 1.2.0), `citation.bib`, `CHANGELOG.md`.
- Theme: applied Hugo Coder palette per CLAUDE.md §A6 (`style/style.css`),
  Inter + JetBrains Mono fonts via `style/header.html`.
- Vancouver CSL fetched into `style/vancouver.csl`.

- 2026-05-11 — added book cover (images/cover.png) to Preface, README thumbnail, EPUB cover-image, OG meta; social-preview.png staged for upload (commit e07c3c4)

## 2026-05-11 — Added LLM-use acknowledgment

- 00-acknowledgments.Rmd: added "Use of LLM tools" subsection
  (self-hosted Mistral Le Chat via Ollama/`ollamar` + Copilot in RStudio)
- 95-colophon.Rmd: added one-line pointer to the acknowledgment
- Commit: f124c08

## 2026-05-11 — Comprehensive checkup

- Engine: already bookdown (converted in 3fad190; verified `_quarto.yml` absent).
- Audited structure: 687 chapter entries, 35 first-level headings, 4 parts.
  Wrote `AUDIT.md` mapping every required item from CLAUDE.md §A1 to ✅/⚠️/❌.
- Filled missing front matter: `00-notation.Rmd`, `00-about-the-author.Rmd`.
  Added both to `_bookdown.yml` sequence after `00-acknowledgments.Rmd`.
- Citation verifier (`scripts/verify-citations.R`) refined to tolerate
  book entries without DOI/arXiv/ISBN/URL — matches the inline CI workflow.
  Local run: 0 hard failures, 31 entries flagged for ISBN backfill.
- 31 entries lacking verifiable identifiers (cohen1988, field2018,
  faraway2015, fox2019, agresti2013, agresti2010, harrell2015,
  hollander2014, maxwell2017, kaufman2009, hosmer2013, rousseeuw2005,
  delacre2017, divine2013, fabrigar1999, bishara2012, gueorguieva2004,
  dinno2015, ghasemi2012, sharpe2015, agresti1998, bakeman2005,
  conover1981, newson2002, kendall1938, kerby2014, rstatix, patil2021,
  rosseel2012, sjoberg2021, wickham2019) — flagged for ISBN backfill.
- Final render: `bookdown::gitbook` exit 0; `docs/notation.html`,
  `docs/about-the-author.html`, and `docs/acknowledgments.html` (with
  "Use of LLM tools" subsection) all present; 36 chapter HTMLs.
- HTML output: staying on `bookdown::gitbook`; `bs4_book` 0.46 crashes
  on `tweak_part_screwup` with `# (PART) … {-}` separators. To be
  revisited when bookdown ships a fix or with a custom assignInNamespace
  patch.
- Deferred: whole-book PDF + per-chapter PDFs (require local tinytex
  setup — CI builds these on push); `v1.0.0` GitHub release + Zenodo DOI
  (depends on PDF/EPUB assets verified by CI).
