knitr::opts_chunk$set(
  echo       = TRUE,
  eval       = FALSE,
  message    = FALSE,
  warning    = FALSE,
  cache      = FALSE,
  fig.align  = "center",
  fig.width  = 7,
  fig.height = 4.5,
  fig.retina = 2,
  dpi        = 300,
  out.width  = "90%",
  comment    = "#>"
)

options(
  scipen = 999,
  digits = 3,
  knitr.kable.NA = "—"
)

set.seed(42)

# bookdown 0.46 bs4_book bug: tweak_part_screwup() trips on
# `if (xml_attr(parent, "class") == "row")` when the parent div has
# no class attr (NA == "row" -> NA -> if() error). The tweak is a
# cosmetic part-heading reflow; no-oping it lets the render complete
# cleanly. Drop the patch once bookdown ships a fix.
if (requireNamespace("bookdown", quietly = TRUE) &&
    "tweak_part_screwup" %in% ls(asNamespace("bookdown"), all.names = TRUE)) {
  utils::assignInNamespace(
    "tweak_part_screwup",
    function(html) invisible(NULL),
    ns = "bookdown"
  )
}

# Citation files copy hook — see refinement §3.3
if (file.exists("citation.bib")) {
  dir.create("docs/citation-files", recursive = TRUE, showWarnings = FALSE)
  file.copy("citation.bib", "docs/citation-files/citation.bib", overwrite = TRUE)
  if (file.exists("citation.ris")) {
    file.copy("citation.ris", "docs/citation-files/citation.ris", overwrite = TRUE)
  }
}

if (requireNamespace("ggplot2", quietly = TRUE)) {
  ggplot2::theme_set(
    ggplot2::theme_minimal(base_size = 12) +
      ggplot2::theme(
        plot.title.position   = "plot",
        plot.caption.position = "plot",
        plot.caption          = ggplot2::element_text(hjust = 0, color = "#666"),
        panel.grid.minor      = ggplot2::element_blank()
      )
  )
}
