suppressPackageStartupMessages({
  library(yaml)
  library(stringr)
})

cfg <- yaml::read_yaml("_bookdown.yml")
files <- cfg$rmd_files
parts <- list()
current_part <- "Front matter"
parts[[current_part]] <- character()

for (f in files) {
  if (str_starts(basename(f), "_part-")) {
    title <- str_remove(readLines(f, n = 1), "^# \\(PART\\) ") |>
      str_remove("\\s*\\{-\\}\\s*$")
    current_part <- title
    if (is.null(parts[[current_part]])) parts[[current_part]] <- character()
    next
  }
  yaml_block <- character()
  on <- FALSE
  for (l in readLines(f, n = 30, warn = FALSE)) {
    if (l == "---") { if (!on) { on <- TRUE; next } else break }
    if (on) yaml_block <- c(yaml_block, l)
  }
  ttl <- ""
  for (l in yaml_block) {
    m <- str_match(l, '^title:\\s*"(.+)"\\s*$')
    if (!is.na(m[1,1])) { ttl <- m[1,2]; break }
  }
  if (ttl == "") ttl <- str_remove(basename(f), "\\.Rmd$")
  parts[[current_part]] <- c(parts[[current_part]], ttl)
}

cat("## Table of contents\n\n")
for (p in names(parts)) {
  if (length(parts[[p]]) == 0) next
  cat("### ", p, "\n\n", sep = "")
  for (t in parts[[p]]) cat("- ", t, "\n", sep = "")
  cat("\n")
}
