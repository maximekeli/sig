#!/usr/bin/env bash
# Compile le rapport LaTeX en PDF
set -euo pipefail
cd "$(dirname "$0")"

TEX="RAPPORT_FONCTIONNALITES_SIG_SOLS.tex"
OUT="RAPPORT_FONCTIONNALITES_SIG_SOLS.pdf"

if ! command -v pdflatex >/dev/null 2>&1; then
  echo "pdflatex absent. Installez TeX Live :"
  echo "  sudo apt install texlive-latex-recommended texlive-latex-extra texlive-lang-french"
  exit 1
fi

echo "Compilation LaTeX (2 passes)…"
pdflatex -interaction=nonstopmode "$TEX" >/dev/null
pdflatex -interaction=nonstopmode "$TEX" >/dev/null

if [[ -f "$OUT" ]]; then
  echo "PDF généré : $(pwd)/$OUT"
  ls -lh "$OUT"
else
  echo "Échec compilation — voir ${TEX%.tex}.log"
  exit 1
fi
