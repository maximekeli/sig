#!/usr/bin/env bash
# Recrée le conteneur web pour charger .env (Sentinel Hub) et vérifie l'API.
set -euo pipefail
cd "$(dirname "$0")/.."

dc() {
  if docker compose "$@" 2>/dev/null; then return 0; fi
  sudo docker compose "$@"
}

echo "==> Arrêt conteneurs web orphelins…"
for c in dusol_sig_web 3211a08c249c_dusol_sig_web 904eca994559_dusol_sig_web dusol_projet-web-1; do
  docker rm -f "$c" 2>/dev/null || sudo docker rm -f "$c" 2>/dev/null || true
done

echo "==> Recréation web + nginx (charge .env)…"
dc down web 2>/dev/null || true
dc up -d --force-recreate --remove-orphans web nginx

echo "==> Attente démarrage…"
sleep 8

echo "==> Variables Sentinel dans le conteneur :"
dc exec -T web env | grep '^SENTINEL_HUB_CLIENT' || true

echo "==> Test manage.py test_sentinel_hub"
dc exec -T web python manage.py test_sentinel_hub

echo "==> Test API publique"
curl -sf http://localhost:8081/api/v1/sentinel/status/ | python3 -m json.tool

echo ""
echo "OK — Sentinel Hub opérationnel sur http://localhost:8081"
