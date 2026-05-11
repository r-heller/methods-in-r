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
