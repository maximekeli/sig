#!/usr/bin/env bash
# Charge .env dans le conteneur web (/opt/dusol.env) et vérifie Sentinel Hub.
# Recréation complète (recommandé) : sudo docker compose up -d --force-recreate web nginx
set -euo pipefail
cd "$(dirname "$0")/.."

dc() {
  if docker compose "$@" 2>/dev/null; then return 0; fi
  sudo docker compose "$@"
}

WEB=$(docker ps --format '{{.Names}}' | grep -E 'sig_web|dusol.*web' | grep -v celery | head -1 || true)
if [ -z "$WEB" ]; then
  echo "Aucun conteneur web actif. Lancez : docker compose up -d web nginx"
  exit 1
fi

echo "==> Copie .env → $WEB:/opt/dusol.env"
docker cp .env "$WEB:/opt/dusol.env" 2>/dev/null || sudo docker cp .env "$WEB:/opt/dusol.env"

if [ "${1:-}" = "--recreate" ]; then
  echo "==> Recréation web + nginx (monte .env en volume)…"
  for c in dusol_sig_web 3211a08c249c_dusol_sig_web 904eca994559_dusol_sig_web; do
    docker rm -f "$c" 2>/dev/null || sudo docker rm -f "$c" 2>/dev/null || true
  done
  dc up -d --force-recreate --remove-orphans web nginx
  WEB=$(docker ps --format '{{.Names}}' | grep -E 'sig_web' | head -1)
  sleep 12
fi

echo "==> Test Sentinel (conteneur $WEB)"
docker exec "$WEB" python manage.py test_sentinel_hub \
  || sudo docker exec "$WEB" python manage.py test_sentinel_hub

echo "==> Test API http://localhost:8081"
curl -sf http://localhost:8081/api/v1/sentinel/status/ | python3 -m json.tool

echo ""
echo "OK — Sentinel Hub opérationnel."
