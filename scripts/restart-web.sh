#!/usr/bin/env bash
# Redémarre un seul conteneur web (évite les doublons qui bloquent /admin/).
set -e
cd "$(dirname "$0")/.."

echo "==> Arrêt des anciens conteneurs web (doublons)..."
docker ps -a --format '{{.Names}}' | grep -E 'web|dusol_web' | while read -r name; do
  docker rm -f "$name" 2>/dev/null || sudo docker rm -f "$name" 2>/dev/null || true
done

echo "==> Démarrage dusol_web + nginx..."
docker compose up -d --build --force-recreate web nginx

echo "==> Vérification /admin/login/ ..."
sleep 3
curl -sf -m 10 -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8081/admin/login/

echo ""
echo "Admin : http://localhost:8081/admin/"
echo "Compte : admin / admin123"
