#!/usr/bin/env bash
# Redémarre le backend avec les routes assistant IA (corrige le 404 Not Found).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Arrêt des anciens conteneurs web…"
docker rm -f dusol_web 2>/dev/null || sudo docker rm -f dusol_web 2>/dev/null || true
docker compose down web 2>/dev/null || sudo docker compose down web 2>/dev/null || true

echo "==> Reconstruction image web…"
docker compose build web || sudo docker compose build web

echo "==> Démarrage web + nginx…"
docker compose up -d --force-recreate --remove-orphans web nginx \
  || sudo docker compose up -d --force-recreate --remove-orphans web nginx

sleep 4
echo "==> Test /api/v1/assistant/status/"
curl -sf http://localhost:8081/api/v1/assistant/status/ && echo || {
  echo "ERREUR: l'API assistant ne répond pas."
  exit 1
}
