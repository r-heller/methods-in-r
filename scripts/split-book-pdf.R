# scripts/split-book-pdf.R
#
# After bookdown::pdf_book has produced docs/methods-in-r.pdf, slice it
# into per-chapter PDFs named to match the bs4_book HTML slugs the UI
# links to (`pdf-chapters/<slug>.pdf`).
#
# Approach:
#  1. Read the PDF outline (pdftools::pdf_toc).
#  2. For each docs/<slug>.html that bs4_book produced, extract its
#     <h1> text — this is the chapter title bookdown wrote into both
#     the outline AND the per-chapter HTML.
#  3. Match outline entries → HTML slugs by normalised title.
#  4. qpdf-subset the page range for each match into
#     docs/pdf-chapters/<slug>.pdf.
#
# No CI dependency beyond pdftools + qpdf, both pre-built CRAN binaries.

suppressPackageStartupMessages({
  if (!requireNamespace("pdftools", quietly = TRUE)) install.packages("pdftools")
  if (!requireNamespace("qpdf",     quietly = TRUE)) install.packages("qpdf")
  if (!requireNamespace("xml2",     quietly = TRUE)) install.packages("xml2")
  library(pdftools)
  library(qpdf)
  library(xml2)
})

book_pdf <- "docs/methods-in-r.pdf"
if (!file.exists(book_pdf)) {
  message("split-book-pdf: ", book_pdf, " not found; skipping")
  quit(status = 0)
}

out_dir <- "docs/pdf-chapters"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

normalise <- function(s) {
  s <- tolower(s)
  s <- gsub("[[:space:]]+", " ", s)
  s <- gsub("^[[:space:]]+|[[:space:]]+$", "", s)
  # strip any leading "1 ", "1.1 ", "chapter 1 ", etc.
  s <- gsub("^chapter\\s+\\d+(\\.\\d+)*\\s*[—:.\\-]?\\s*", "", s)
  s <- gsub("^\\d+(\\.\\d+)*\\s*[—:.\\-]?\\s*", "", s)
  s
}

# 1) Build slug -> normalised title from rendered HTML
html_files <- list.files("docs", pattern = "\\.html$", full.names = TRUE)
html_files <- html_files[!grepl("(^|/)404\\.html$", html_files)]
html_files <- html_files[!grepl("/libs/",   html_files)]
slug_titles <- list()
for (f in html_files) {
  doc <- tryCatch(read_html(f, options = "RECOVER"), error = function(e) NULL)
  if (is.null(doc)) next
  h1 <- xml_find_first(doc, "//main//h1 | //div[@id='header']//h1.title | //h1[1]")
  if (inherits(h1, "xml_missing") || is.na(h1)) next
  t <- xml_text(h1, trim = TRUE)
  if (!nzchar(t)) next
  slug <- tools::file_path_sans_ext(basename(f))
  slug_titles[[slug]] <- normalise(t)
}
title_to_slug <- setNames(names(slug_titles), unlist(slug_titles))

# 2) Walk PDF outline; for each top-level entry, find slug + page range
toc <- pdftools::pdf_toc(book_pdf)
n_pages <- pdftools::pdf_info(book_pdf)$pages

# pdftools::pdf_toc returns a nested list. Flatten top-level children only.
top <- toc$children
if (is.null(top) || length(top) == 0) {
  message("split-book-pdf: no top-level outline entries; skipping")
  quit(status = 0)
}

# Each entry: list(title, page, children) — we need title + page
entries <- lapply(top, function(e) list(title = e$title, page = e$page))
# Sort by page (outline is usually in order, but ensure)
entries <- entries[order(vapply(entries, function(e) e$page %||% NA_integer_, integer(1)))]

`%||%` <- function(a, b) if (is.null(a) || is.na(a)) b else a

made <- character(0)
skipped <- character(0)

for (i in seq_along(entries)) {
  e <- entries[[i]]
  start <- as.integer(e$page %||% NA)
  if (is.na(start)) next
  end <- if (i < length(entries)) {
    as.integer(entries[[i + 1]]$page %||% NA) - 1L
  } else {
    n_pages
  }
  if (is.na(end) || end < start) end <- start

  norm <- normalise(e$title)
  slug <- title_to_slug[[norm]]

  if (is.null(slug) || !nzchar(slug)) {
    # Try a looser match: substring containment in either direction
    cand <- names(title_to_slug)[
      vapply(names(title_to_slug),
             function(t) grepl(norm, t, fixed = TRUE) || grepl(t, norm, fixed = TRUE),
             logical(1))
    ]
    if (length(cand) == 1) slug <- title_to_slug[[cand]]
  }

  if (is.null(slug) || !nzchar(slug)) {
    skipped <- c(skipped, paste0("[", start, "-", end, "] ", e$title))
    next
  }

  out_file <- file.path(out_dir, paste0(slug, ".pdf"))
  ok <- tryCatch({
    qpdf::pdf_subset(book_pdf, pages = start:end, output = out_file)
    TRUE
  }, error = function(err) {
    message("FAILED split for ", slug, ": ", conditionMessage(err))
    FALSE
  })
  if (ok) made <- c(made, slug)
}

cat("split-book-pdf: produced", length(made), "per-chapter PDFs\n")
if (length(skipped)) {
  cat("split-book-pdf: skipped (no slug match):\n")
  cat(paste0("  - ", skipped, "\n"), sep = "")
}
