# Research paper

`facilitiesHelp.tex` — the full methodology paper (data profiling, trust engine, validation,
medical-desert / supply–demand, correlation, causal inference with formulas, statistical ML &
geometric DL, geospatial). Every statistic is computed live from the gold tables.

## Build (Overleaf — easiest)
1. New Project → Upload Project, or upload `facilitiesHelp.tex` **and the repo's `figures/` folder**.
2. The preamble sets `\graphicspath{{../figures/}}`; on Overleaf put `figures/` next to the `.tex`
   (or change the path to `{{figures/}}`). Compile with pdfLaTeX.

## Build (local)
```bash
brew install --cask mactex-no-gui   # or: tlmgr / tectonic
cd paper && pdflatex facilitiesHelp.tex && pdflatex facilitiesHelp.tex
```
