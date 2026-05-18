#!/usr/bin/env bash
# Configure l'environnement Python local pour Cursor / VS Code (supprime les erreurs rouges).
set -e
cd "$(dirname "$0")/../backend"

echo "==> Création du venv backend/.venv"
python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip

echo "==> Installation des dépendances (peut prendre quelques minutes)..."
.venv/bin/pip install -q \
  Django djangorestframework djangorestframework-gis djangorestframework-simplejwt \
  django-cors-headers django-filter channels channels-redis daphne \
  celery redis pytest pytest-django pytest-cov factory-boy \
  django-stubs djangorestframework-stubs \
  Pillow python-dotenv gunicorn psycopg2-binary scikit-learn numpy pandas joblib \
  earthaccess pystac-client shapely xarray 2>/dev/null || true

echo ""
echo "==> Terminé."
echo "Dans Cursor : Ctrl+Shift+P → Python: Select Interpreter"
echo "  → Choisir : backend/.venv/bin/python"
echo "Puis : Developer: Reload Window"
