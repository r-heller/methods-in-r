# Structural Audit — Methods in R

Date: 2026-05-11
Branch: `audit/structure`
Operator: Claude Code (autonomous), per the in-session Comprehensive Bookdown
Repo Check-Up & Publish procedure.

## Engine

✅ **Bookdown** — `_bookdown.yml` + `index.Rmd` present; no `_quarto.yml`.
Conversion from Quarto was completed in commit `3fad190` (see `GENERATION_LOG.md`).

## Inventory

### Top-level configuration

| File           | Status | Notes                                                                              |
|----------------|--------|------------------------------------------------------------------------------------|
| `index.Rmd`    | ✅     | YAML matches §A2: title/subtitle/author/`site: bookdown::bookdown_site`, `documentclass: book`, bibliography `[references.bib, packages.bib]`, `csl: style/vancouver.csl`, `link-citations: yes`, `github-repo`, `url`, `description`, `cover-image`. |
| `_bookdown.yml`| ✅     | `book_filename: "methods-in-r"`, `delete_merged_file: true`, `output_dir: "docs"`, `new_session: no`, `before_chapter_script: "_common.R"`, `rmd_subdir: true`, explicit `rmd_files` list of 687 entries. |
| `_output.yml`  | ⚠️     | Currently `bookdown::gitbook` (HTML) + `bookdown::pdf_book` + `bookdown::epub_book`. CLAUDE.md §A2 prefers `bs4_book`; switched away because `bs4_book` 0.46 trips on `tweak_part_screwup` with PART separator files. Will retry with `# (PART\*)` workaround in Phase 2. |
| `_common.R`    | ✅     | knitr options match §A3 (eval=FALSE globally — book is static-render per the upstream conversion); ggplot2 `theme_minimal` set; seed 42. |

### Body

- **Chapters:** 687 `.Rmd` entries listed in `_bookdown.yml`, organised into 4 parts (`_part-foundations.Rmd`, `_part-modelling.Rmd`, `_part-applications.Rmd`, `_part-reporting-templates.Rmd`) via `# (PART) … {-}` separator files.
- **Chapter index files (16):** `chapters/<NN-topic>/index.Rmd` each carry a chapter-level H1 with `{#sec-ch-NN-…}` anchor.
- **Method pages (~560):** each is a YAML-titled `.Rmd` with H2 body; they fold under their parent chapter's H1 by design.
- **Lab pages (80):** under `chapters/<topic>/labs/*.Rmd`.

### Front matter

| File                       | Status | Notes                                                           |
|----------------------------|--------|-----------------------------------------------------------------|
| `00-impressum.Rmd`         | ✅     | Copyright, CC BY-SA 4.0, suggested citation, disclaimer, contact. |
| `00-acknowledgments.Rmd`   | ✅     | Tooling + LLM-use subsection (commit `f124c08`).                |
| `how-to-use.Rmd`           | ⚠️     | Present at repo root but not under `00-` prefix. Sidebar position is correct via explicit `_bookdown.yml` ordering. **Not renaming** to avoid churning 687 cross-links. |
| `ch00-find-your-method.Rmd`| ✅     | Decision tree, anchored `{#sec-find-your-method}`.              |
| `00-preface.Rmd`           | n/a    | Preface lives inside `index.Rmd` (§5.1 allows this).            |
| `00-notation.Rmd`          | ❌     | Missing — adding minimal stub in this phase.                    |
| `00-about-the-author.Rmd`  | ❌     | Missing — adding minimal stub in this phase.                    |

### Back matter

| File                | Status | Notes                                                                |
|---------------------|--------|----------------------------------------------------------------------|
| `90-glossary.Rmd`   | ⚠️     | Glossary lives at `appendices/B-glossary.Rmd`; adding a `90-glossary.Rmd` at the root would duplicate. Keeping the appendix version; not adding a redundant 90-glossary stub. |
| `95-colophon.Rmd`   | ✅     | Build info + sessioninfo + LLM-use one-liner.                         |
| `99-references.Rmd` | ✅     | Single `<div id="refs"></div>` block, unnumbered.                     |

### Infrastructure

| File                                  | Status | Notes                                                       |
|---------------------------------------|--------|-------------------------------------------------------------|
| `style/style.css`                     | ✅     | Hugo Coder palette per §A6; dark-mode override; callouts.   |
| `style/header.html`                   | ✅     | Inter + JetBrains Mono via Google Fonts.                    |
| `style/preamble.tex`                  | ✅     | `microtype`, `booktabs`, `longtable`, `xcolor` (`linkblue #1565C0`), `fontspec` (Inter / JetBrains Mono). |
| `style/vancouver.csl`                 | ✅     | Vancouver style (biomedical default).                       |
| `style/per-chapter-pdf-button.html`   | ✅     | Click handler that wires the per-chapter PDF buttons.       |
| `renv.lock`                           | ✅     | Present at repo root.                                       |
| `.Rprofile`                           | ✅     | Guarded `if (file.exists("renv/activate.R")) source(...)`.  |
| `CITATION.cff`                        | ✅     | CFF 1.2.0; license `CC-BY-SA-4.0` to match `LICENSE-CONTENT`. |
| `citation.bib`                        | ✅     | Matches CITATION.cff.                                       |
| `LICENSE`                             | ✅     | MIT (code).                                                 |
| `LICENSE-CONTENT`                     | ✅     | CC BY-SA 4.0 (book prose). Deviates from CLAUDE.md default (CC BY 4.0); preserved from prior remote commit to respect existing licence choice. |
| `images/cover.png`                    | ✅     | 1280×2043, extracted from `Methods in R - Book Cover.pdf`.  |
| `.github/social-preview.png`          | ✅     | 1280×640 landscape — needs manual upload via repo Settings → Social preview. |
| `book.bib`                            | ❌→n/a  | Repo uses `references.bib` (279 lines, 100+ entries). `index.Rmd` `bibliography:` field already points to it. Not renaming to avoid breaking cross-refs and CI. |
| `packages.bib`                        | ✅     | Auto-generated during render (`knitr::write_bib(...)` chunk in `index.Rmd`). |

### CI workflows

| File                                       | Status | Notes                                                                 |
|--------------------------------------------|--------|-----------------------------------------------------------------------|
| `.github/workflows/render-book.yml`        | ✅     | Renders all formats + per-chapter PDFs, deploys `docs/` to `gh-pages` via `JamesIves/github-pages-deploy-action@v4`. |
| `.github/workflows/citation-check.yml`     | ✅     | 116-line inline R script verifying DOIs, arXiv IDs, PMIDs on push/PR. |

### README

✅ Polished per §6.1: centered cover thumbnail (link-wrapped), no badges, downloads (PDF/EPUB), 16-topic overview, BibTeX citation block, reproducibility recipe, license, contributing link.

## Numbering & TOC sanity

- Exactly one H1 per chapter-index file (16 topic chapters + reporting + appendices). Method pages have no H1 by design; they fold into their parent chapter (intentional).
- No H2→H4 level skipping observed in spot checks on `chapters/01-foundations/*.Rmd`.
- `number_sections` is not disabled anywhere.
- `bs4_book` would produce numbered hierarchical sidebar (`1`, `1.1`, `1.1.1`) once the PART-screwup workaround is in place; `gitbook` (current) produces the same numbering but in a different sidebar style.

## Stubs created this phase

- `00-notation.Rmd` (symbol + abbreviation table — minimal stub).
- `00-about-the-author.Rmd` (short bio stub).

## Deferred (out of scope this checkup)

- Renaming `references.bib` → `book.bib` (cross-link churn not worth it).
- Renaming `how-to-use.Rmd` → `00-how-to-use.Rmd` (same reason).
- `00-preface.Rmd` as a standalone file (preface lives in `index.Rmd` and §5.1 allows this).
- `90-glossary.Rmd` at repo root (glossary in `appendices/B-glossary.Rmd`).
- `CLAUDE.md` committed to repo (globally gitignored by user's standing rule "no Claude-specific files in repositories").
- Whole-book PDF render and per-chapter PDFs (texlive setup; this checkup verifies HTML + EPUB; CI builds PDF on push).
- Zenodo DOI / `v1.0.0` GitHub release (depends on whole-book PDF / EPUB assets; can be done after CI verifies the full toolchain).
