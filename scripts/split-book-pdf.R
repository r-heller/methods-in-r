# scripts/split-book-pdf.R
#
# Slice docs/methods-in-r.pdf into per-chapter PDFs named to match the
# bs4_book HTML slugs (so the UI's pdf-chapters/<slug>.pdf links resolve).
#
# Strategy: the PDF outline (bookmarks) gives chapter titles + named
# destinations. We invoke a small Python helper that uses pypdf to
# resolve those destinations to page numbers; then in R we map the
# chapter titles to HTML slugs via the rendered docs/*.html <h1>s and
# qpdf::pdf_subset() each chapter's page range.

suppressPackageStartupMessages({
  library(qpdf)
  library(xml2)
  library(jsonlite)
})

book_pdf <- "docs/methods-in-r.pdf"
if (!file.exists(book_pdf)) {
  message("split-book-pdf: ", book_pdf, " not found; skipping")
  quit(status = 0)
}

out_dir <- "docs/pdf-chapters"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

clean <- function(s) {
  s <- tolower(s)
  s <- gsub("[[:space:]]+", " ", s)
  s <- gsub("^[[:space:]]+|[[:space:]]+$", "", s)
  s <- gsub("^chapter\\s+\\d+(\\.\\d+)*\\s*[—–:.\\-]?\\s*", "", s)
  s <- gsub("^appendix\\s+[a-z]\\s*[—–:.\\-]?\\s*", "", s)
  s <- gsub("^\\d+(\\.\\d+)*\\s*[—–:.\\-]?\\s*", "", s)
  s
}

# 1) slug -> cleaned title from rendered HTML
html_files <- list.files("docs", pattern = "\\.html$", full.names = TRUE)
html_files <- html_files[!grepl("(^|/)404\\.html$", html_files)]
html_files <- html_files[!grepl("/libs/", html_files)]

slug_title <- list()
for (f in html_files) {
  doc <- tryCatch(read_html(f, options = "RECOVER"), error = function(e) NULL)
  if (is.null(doc)) next
  h1 <- xml_find_first(doc, "//main//h1[1] | //h1[1]")
  if (inherits(h1, "xml_missing")) next
  raw <- xml_text(h1, trim = TRUE)
  if (!nzchar(raw)) next
  slug <- tools::file_path_sans_ext(basename(f))
  slug_title[[slug]] <- clean(raw)
}
cat("split-book-pdf: ", length(slug_title), " HTML slugs to match\n", sep = "")

# 2) Call Python pypdf to extract outline -> page number map.
py <- "
import sys, json
from pypdf import PdfReader
r = PdfReader(sys.argv[1])
out = []
# Top-level entries only; nested lists are sub-sections (H2/H3) we skip.
for it in r.outline:
    if isinstance(it, list):
        continue
    title = getattr(it, 'title', None)
    if not title:
        continue
    try:
        p = r.get_destination_page_number(it) + 1
    except Exception:
        continue
    out.append({'title': title, 'page': p})
print(json.dumps(out))
"
tmp <- tempfile(fileext = ".py")
writeLines(py, tmp)
py_bin <- Sys.which("python3")
if (!nzchar(py_bin)) py_bin <- Sys.which("python")
if (!nzchar(py_bin)) {
  cat("split-book-pdf: no python on PATH; skipping\n")
  quit(status = 0)
}
res <- system2(py_bin, c(tmp, book_pdf), stdout = TRUE, stderr = TRUE)
unlink(tmp)
if (length(res) == 0 || !nzchar(res[length(res)])) {
  cat("split-book-pdf: pypdf produced no outline; skipping\n")
  quit(status = 0)
}
outline <- jsonlite::fromJSON(res[length(res)], simplifyDataFrame = TRUE)
cat("split-book-pdf: outline has ", nrow(outline), " entries\n", sep = "")

# 3) Match outline titles -> slug (safe lookup with single-bracket)
title_to_slug <- setNames(names(slug_title), unlist(slug_title))
outline$clean <- vapply(outline$title, clean, character(1))
outline$slug  <- unname(title_to_slug[outline$clean])

matched <- outline[!is.na(outline$slug), c("slug", "title", "page")]
matched <- matched[order(matched$page), ]
cat("split-book-pdf: matched ", nrow(matched), " of ", nrow(outline),
    " outline entries\n", sep = "")

if (!nrow(matched)) {
  cat("split-book-pdf: no slug matches — first 10 outline titles:\n")
  cat(paste0("  - ", head(outline$title, 10), " [", head(outline$clean, 10), "]\n"), sep = "")
  cat("split-book-pdf: first 10 slug titles:\n")
  cat(paste0("  - ", head(unlist(slug_title), 10), "\n"), sep = "")
  quit(status = 0)
}

# 4) page ranges + qpdf subset
n_pages <- as.integer(system2("qpdf", c("--show-npages", book_pdf), stdout = TRUE))
matched$end <- c(matched$page[-1] - 1L, n_pages)

made <- 0L; failed <- character(0)
for (i in seq_len(nrow(matched))) {
  out_file <- file.path(out_dir, paste0(matched$slug[i], ".pdf"))
  rng <- matched$page[i]:matched$end[i]
  ok <- tryCatch({
    qpdf::pdf_subset(book_pdf, pages = rng, output = out_file)
    TRUE
  }, error = function(e) {
    failed <<- c(failed, paste0(matched$slug[i], ": ", conditionMessage(e)))
    FALSE
  })
  if (ok) made <- made + 1L
}

cat("split-book-pdf: produced ", made, " per-chapter PDFs\n", sep = "")
if (length(failed)) {
  cat("split-book-pdf: failures:\n")
  cat(paste0("  - ", failed, "\n"), sep = "")
}
unmatched_slugs <- setdiff(names(slug_title), matched$slug)
if (length(unmatched_slugs)) {
  cat("split-book-pdf: slugs with no outline match:\n")
  cat(paste0("  - ", unmatched_slugs, "\n"), sep = "")
}
