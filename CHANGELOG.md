# Changelog

All notable changes to this book are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
semver-ish (major bump on substantive content reorganisation; minor bump on
new chapters or sections; patch bump on errata).

## [1.0.0] — 2026-05-11

Initial bookdown release.

### Migrated

- Converted the book from Quarto (`.qmd`) to bookdown (`.Rmd`):
  - 680 source files converted with cross-ref, callout, and chunk-fence
    syntax transforms.
  - New build scaffold: `index.Rmd`, `_bookdown.yml`, `_output.yml`,
    `_common.R`, `style/{style.css,header.html,preamble.tex,
    per-chapter-pdf-button.html,vancouver.csl}`.
  - CI workflow replaced: `.github/workflows/render-book.yml` builds
    bs4_book HTML + PDF + EPUB and deploys to `gh-pages`.

### Added

- Hugo Coder palette applied via `style/style.css` (light + dark).
- Front matter: `00-impressum.Rmd`, `00-acknowledgments.Rmd`.
- Back matter: `95-colophon.Rmd`, `99-references.Rmd`.
- Per-chapter PDF download button via `style/per-chapter-pdf-button.html`
  and `scripts/render-chapter-pdfs.R`.
- `CITATION.cff` + `citation.bib`.
- `scripts/verify-citations.R` and `.github/workflows/citation-check.yml`.

### Editorial

- Removed direct references to the source-repo course/week/session
  structure (CTTIR/courses) from titles, lab YAML, prerequisites,
  cross-link labels, chapter-index tables, and the cheatsheets appendix.
- Cheatsheets renamed by topic instead of by course/week.
