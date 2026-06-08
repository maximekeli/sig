# Rapport fonctionnel SIG Sols Togo (LaTeX)

## Fichiers

| Fichier | Description |
|---------|-------------|
| `RAPPORT_FONCTIONNALITES_SIG_SOLS.tex` | Source LaTeX complète (architecture, API, web, mobile, admin) |
| `compile-rapport.sh` | Script de compilation PDF |

## Générer le PDF

```bash
# Installer TeX Live (une fois)
sudo apt install texlive-latex-recommended texlive-latex-extra texlive-lang-french texlive-fonts-recommended

# Compiler
cd docs/rapport
./compile-rapport.sh
```

Le PDF est produit : `RAPPORT_FONCTIONNALITES_SIG_SOLS.pdf`

## Contenu du rapport

- Page de garde stylisée (couleurs DUSOL)
- Architecture globale (schémas TikZ)
- Cartographie : 3 fonds (OSM, satellite, topographique), parcelles, couches
- Inventaire complet des endpoints API
- Modules web PWA et mobile Flutter
- Administration, Celery, APIs externes
- Synthèse modulaire
