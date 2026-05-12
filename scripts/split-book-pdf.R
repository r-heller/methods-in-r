# scripts/split-book-pdf.R
#
# After bookdown::pdf_book has produced docs/methods-in-r.pdf, slice it
# into per-chapter PDFs named to match the bs4_book HTML slugs the UI
# links to (`pdf-chapters/<slug>.pdf`).
#
# pdftools::pdf_toc returns titles but no page numbers (PDF destinations
# are named anchors, not page integers), so we instead scan every page's
# text for the chapter title and use the first hit as the chapter start.
#
# Approach:
#  1. Build a mapping slug -> chapter-title from each docs/*.html's <h1>.
#  2. pdf_text(book_pdf) returns one string per page. For each chapter
#     title, find the first page whose text contains it (numbered prefix
#     stripped first).
#  3. Sort chapters by start page; end page = next chapter's start - 1.
#  4. qpdf::pdf_subset() each range into docs/pdf-chapters/<slug>.pdf.

suppressPackageStartupMessages({
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

clean <- function(s) {
  s <- tolower(s)
  s <- gsub(" ", " ", s, fixed = TRUE)
  s <- gsub("[[:space:]]+", " ", s)
  s <- gsub("^[[:space:]]+|[[:space:]]+$", "", s)
  # strip any leading "1 ", "1.1 ", "chapter 1 ", "appendix a ", roman prefixes
  s <- gsub("^chapter\\s+\\d+(\\.\\d+)*\\s*[—:.\\-]?\\s*", "", s)
  s <- gsub("^appendix\\s+[a-z]\\s*[—:.\\-]?\\s*", "", s)
  s <- gsub("^\\d+(\\.\\d+)*\\s*[—:.\\-]?\\s*", "", s)
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

# 2) Per-page text grouped by font height. Chapter-heading pages have
# the chapter title rendered in big text (height >= 18pt); TOC entries
# are ~10pt. Scanning only the large-text content rules out TOC matches.
data <- pdftools::pdf_data(book_pdf)
n_pages <- length(data)
HEIGHT_THRESHOLD <- 18  # PDF user-units; bookdown's chapter heading is much bigger

page_big_text <- vapply(seq_along(data), function(i) {
  df <- data[[i]]
  if (is.null(df) || !nrow(df) || !"height" %in% names(df)) return("")
  big <- df[!is.na(df$height) & df$height >= HEIGHT_THRESHOLD, ]
  if (!nrow(big)) return("")
  clean(paste(big$text, collapse = " "))
}, character(1))

# 3) for each slug, first page whose LARGE-TEXT contains the title
matches <- list()
for (slug in names(slug_title)) {
  title <- slug_title[[slug]]
  if (nchar(title) < 3) next
  hit <- which(vapply(page_big_text,
                      function(p) grepl(title, p, fixed = TRUE),
                      logical(1)))
  if (length(hit) == 0) next
  matches[[slug]] <- min(hit)
}
cat("split-book-pdf: matched ", length(matches), " chapters to pages\n", sep = "")

if (length(matches) == 0) {
  cat("split-book-pdf: no matches — skipping\n")
  quit(status = 0)
}

# 4) sort by start page, derive end pages, subset
df <- data.frame(
  slug  = names(matches),
  start = unlist(matches, use.names = FALSE),
  stringsAsFactors = FALSE
)
df <- df[order(df$start), ]
df$end <- c(df$start[-1] - 1L, n_pages)

made <- 0L; failed <- character(0)
for (i in seq_len(nrow(df))) {
  out_file <- file.path(out_dir, paste0(df$slug[i], ".pdf"))
  rng <- df$start[i]:df$end[i]
  ok <- tryCatch({
    qpdf::pdf_subset(book_pdf, pages = rng, output = out_file)
    TRUE
  }, error = function(e) {
    failed <<- c(failed, paste0(df$slug[i], ": ", conditionMessage(e)))
    FALSE
  })
  if (ok) made <- made + 1L
}

cat("split-book-pdf: produced ", made, " per-chapter PDFs\n", sep = "")
if (length(failed)) {
  cat("split-book-pdf: failures:\n")
  cat(paste0("  - ", failed, "\n"), sep = "")
}
unmatched <- setdiff(names(slug_title), names(matches))
if (length(unmatched)) {
  cat("split-book-pdf: unmatched slugs (no title text on any page):\n")
  cat(paste0("  - ", unmatched, "\n"), sep = "")
}
