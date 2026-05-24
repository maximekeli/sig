#!/usr/bin/env bash
# Redémarre le backend avec .env à jour (clé Gemini + modèle).
set -euo pipefail
cd "$(dirname "$0")/.."

dc() {
  if docker compose "$@" 2>/dev/null; then return 0; fi
  sudo docker compose "$@"
}

echo "Modèle recommandé : gemini-2.5-flash-lite (quota gratuit)"
grep -q '^GEMINI_MODEL=' .env || echo 'GEMINI_MODEL=gemini-2.5-flash-lite' >> .env
echo "==> Arrêt des anciens conteneurs web (sudo si besoin)…"
for c in dusol_sig_web 3211a08c249c_dusol_sig_web 904eca994559_dusol_sig_web \
  dusol_web dusol_projet-web-1 2963aa31d25b_dusol_web; do
  docker rm -f "$c" 2>/dev/null || sudo docker rm -f "$c" 2>/dev/null || true
done
dc down web 2>/dev/null || true

echo "==> Reconstruction image web…"
dc build web

echo "==> Démarrage web + nginx…"
dc up -d --force-recreate --remove-orphans web nginx

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

echo "==> Test Sentinel Hub"
if dc exec -T web python manage.py test_sentinel_hub 2>/dev/null \
  || sudo docker compose exec -T web python manage.py test_sentinel_hub; then
  curl -sf http://localhost:8081/api/v1/sentinel/status/ | head -c 200 && echo
  echo "OK Sentinel Hub"
else
  echo "AVERTISSEMENT: Sentinel Hub — vérifiez SENTINEL_HUB_* dans .env puis : ./scripts/reload-sentinel.sh"
fi

echo "==> Test OpenWeather"
if dc exec -T web python manage.py test_openweather 2>/dev/null \
  || sudo docker compose exec -T web python manage.py test_openweather; then
  curl -sf http://localhost:8081/api/v1/weather/status/ | head -c 200 && echo
  echo "OK OpenWeather"
else
  echo "AVERTISSEMENT: OpenWeather — vérifiez OPENWEATHER_API_KEY dans .env"
fi
