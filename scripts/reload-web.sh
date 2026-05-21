#!/usr/bin/env bash
# Recharge le processus Django/Daphne dans le conteneur web (nouvelles routes API).
set -euo pipefail
cd "$(dirname "$0")/.."
NAME="${WEB_CONTAINER:-dusol_sig_web}"

if ! docker ps --format '{{.Names}}' | grep -qx "$NAME"; then
  NAME=$(docker ps --format '{{.Names}}' | grep -E 'sig_web|dusol.*web' | head -1 || true)
fi

if [ -z "$NAME" ]; then
  echo "Aucun conteneur web trouvé. Lancez : docker compose up -d web"
  exit 1
fi

echo "==> Rechargement de $NAME …"
docker exec "$NAME" python -c "import os, signal; os.kill(1, signal.SIGTERM)" 2>/dev/null \
  || sudo docker exec "$NAME" python -c "import os, signal; os.kill(1, signal.SIGTERM)"

echo "==> Attente redémarrage (30 s)…"
sleep 30

echo "==> Test engagement vidéos"
curl -sf "http://localhost:8081/api/v1/videos/posts/?kind=video" | head -c 80 && echo
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8081/api/v1/videos/posts/1/toggle_like/")
if [ "$CODE" = "401" ] || [ "$CODE" = "200" ]; then
  echo "OK toggle_like → HTTP $CODE (401 sans login = route trouvée)"
else
  echo "ERREUR toggle_like → HTTP $CODE (attendu 401 ou 200, pas 404)"
  exit 1
fi
