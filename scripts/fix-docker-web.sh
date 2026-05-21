#!/usr/bin/env bash
# Redémarre le backend avec .env à jour (clé Gemini + modèle).
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Modèle recommandé : gemini-2.5-flash-lite (quota gratuit)"
grep -q '^GEMINI_MODEL=' .env || echo 'GEMINI_MODEL=gemini-2.5-flash-lite' >> .env
echo "==> Arrêt des anciens conteneurs web (sudo si besoin)…"
docker rm -f dusol_web dusol_projet-web-1 2963aa31d25b_dusol_web 2>/dev/null || true
sudo docker rm -f dusol_web dusol_projet-web-1 2963aa31d25b_dusol_web 2>/dev/null || true
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

echo "==> Test /api/v1/videos/posts/"
curl -sf "http://localhost:8081/api/v1/videos/posts/?kind=video" | head -c 120 && echo || {
  echo "ERREUR: l'API vidéos renvoie 404 — redémarrer le conteneur web (voir ci-dessus)."
  exit 1
}
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8081/api/v1/videos/posts/1/toggle_like/")
if [ "$CODE" = "404" ]; then
  echo "ERREUR: toggle_like introuvable (404) — le backend n'a pas rechargé le code."
  exit 1
fi
echo "OK routes likes/commentaires (toggle_like → HTTP $CODE)"
