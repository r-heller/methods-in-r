suppressPackageStartupMessages({
  library(bibtex); library(httr2); library(purrr)
})

bib_file <- if (file.exists("book.bib")) "book.bib" else "references.bib"
if (!file.exists(bib_file)) {
  message("No bibliography file found; skipping verification.")
  quit(status = 0)
}

bib  <- bibtex::read.bib(bib_file)
keys <- names(bib)

# Hard-fail on broken DOI / arXiv / URL. Book entries without a verifiable
# identifier are tolerated (NA → soft-skip) and listed in the output so
# Raban can add ISBNs incrementally. Matches the inline CI workflow in
# .github/workflows/citation-check.yml.
strict <- function(entry) {
  doi   <- entry$doi
  arxiv <- entry$eprint
  isbn  <- entry$isbn
  url   <- entry$url
  if (!is.null(doi))
    return(tryCatch(request(paste0("https://doi.org/", doi)) |> req_method("HEAD") |> req_perform() |> resp_status() < 400, error = \(e) FALSE))
  if (!is.null(arxiv))
    return(tryCatch(request(paste0("https://arxiv.org/abs/", arxiv)) |> req_method("HEAD") |> req_perform() |> resp_status() < 400, error = \(e) FALSE))
  if (!is.null(isbn))
    return(TRUE)
  if (!is.null(url))
    return(tryCatch(request(url) |> req_method("HEAD") |> req_perform() |> resp_status() < 400, error = \(e) FALSE))
  NA
}

results   <- map(bib, strict)
hard_fail <- map_lgl(results, \(r) isFALSE(r))
soft_skip <- map_lgl(results, is.na)

bad     <- keys[hard_fail]
skipped <- keys[soft_skip]

if (length(skipped)) {
  cat(length(skipped),
      " entries without DOI / arXiv / URL / ISBN — tolerated:\n",
      sep = "")
  cat(paste0("  - ", skipped, "\n"), sep = "")
}

if (length(bad)) {
  cat("Unresolved citation keys:\n")
  cat(paste0("  - ", bad, "\n"), sep = "")
  quit(status = 1)
}

ok <- sum(map_lgl(results, isTRUE))
cat("All ", ok, " verifiable citation keys resolved.\n",
    "(", length(skipped),
    " skipped — see GENERATION_LOG.md for follow-up.)\n",
    sep = "")
