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

check_one <- function(entry) {
  doi   <- entry$doi
  arxiv <- entry$eprint
  isbn  <- entry$isbn
  url   <- entry$url
  if (!is.null(doi))   return(tryCatch(request(paste0("https://doi.org/", doi)) |> req_method("HEAD") |> req_perform() |> resp_status() < 400, error = \(e) FALSE))
  if (!is.null(arxiv)) return(tryCatch(request(paste0("https://arxiv.org/abs/", arxiv)) |> req_method("HEAD") |> req_perform() |> resp_status() < 400, error = \(e) FALSE))
  if (!is.null(isbn))  return(TRUE)
  if (!is.null(url))   return(tryCatch(request(url) |> req_method("HEAD") |> req_perform() |> resp_status() < 400, error = \(e) FALSE))
  FALSE
}

results <- map_lgl(bib, check_one)
bad <- keys[!results]
if (length(bad)) {
  cat("Unresolved citation keys:\n"); cat(paste0("  - ", bad, "\n"))
  quit(status = 1)
}
cat("All ", length(keys), " citation keys resolved.\n")
