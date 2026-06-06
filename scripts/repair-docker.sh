#!/usr/bin/env bash
# Réparation Docker SIG Sols — avec ou sans sudo.
set -uo pipefail
cd "$(dirname "$0")/.."

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
err()  { echo -e "${RED}✗${NC} $1"; }

ping_health() {
  local port="$1"
  curl -sf --max-time "${2:-8}" "http://127.0.0.1:${port}/health/" >/dev/null 2>&1
}

start_emergency_stack() {
  echo "  Démarrage pile d'urgence (web_emergency + nginx :8083)…"
  if ! docker ps --format '{{.Names}}' | grep -q '^dusol_web_emergency$'; then
    docker run -d --name dusol_web_emergency \
      --network dusol_projet_default \
      --network-alias web_emergency \
      -v "$(pwd)/backend:/app" \
      -v "$(pwd)/.env:/opt/dusol.env:ro" \
      -v dusol_projet_media_data:/app/media \
      --env-file .env \
      -e POSTGRES_HOST=db \
      -e REDIS_URL=redis://redis:6379/0 \
      -e REDIS_CACHE_URL=redis://redis:6379/1 \
      -e CELERY_BROKER_URL=redis://redis:6379/0 \
      dusol_projet-web \
      daphne -b 0.0.0.0 -p 8000 config.asgi:application >/dev/null 2>&1 \
      || docker start dusol_web_emergency >/dev/null 2>&1 || true
  else
    docker start dusol_web_emergency >/dev/null 2>&1 || true
  fi

  docker rm -f dusol_nginx_emergency 2>/dev/null || true
  docker run -d --name dusol_nginx_emergency \
    --network dusol_projet_default \
    -p 8083:80 \
    -v "$(pwd)/nginx/nginx-emergency.conf:/etc/nginx/nginx.conf:ro" \
    -v "$(pwd)/frontend:/usr/share/nginx/html/frontend:ro" \
    -v dusol_projet_media_data:/usr/share/nginx/media:ro \
    -v "$(pwd)/backend/staticfiles:/usr/share/nginx/static:ro" \
    --restart unless-stopped \
    nginx:alpine >/dev/null 2>&1

  for i in $(seq 1 20); do
    ping_health 8083 5 && return 0
    sleep 2
  done
  return 1
}

echo "══════════════════════════════════════════════"
echo " Réparation Docker — SIG Sols Togo"
echo "══════════════════════════════════════════════"

echo ""
echo "==> Diagnostic…"
docker ps -a --filter name=dusol --format '  {{.Names}} — {{.Status}}' 2>/dev/null | head -12 || true

WEB_COUNT=$(docker ps --filter name=web --format '{{.Names}}' 2>/dev/null | grep -c dusol || echo 0)
if [ "${WEB_COUNT:-0}" -gt 2 ]; then
  warn "${WEB_COUNT} conteneurs web — risque de blocage (conteneurs root non arrêtables sans sudo)"
fi

WORKING_PORT=""
for port in 8081 8082 8083; do
  if ping_health "$port" 6; then
    WORKING_PORT="$port"
    break
  fi
done

if [ -n "$WORKING_PORT" ]; then
  ok "API opérationnelle sur http://localhost:${WORKING_PORT}"
  curl -sf "http://127.0.0.1:${WORKING_PORT}/health/?detail=1" 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
db=d.get('checks',{}).get('database_info',{})
print('  PostGIS:', db.get('backend'), db.get('name'), '| redis:', d.get('checks',{}).get('redis','?'))
" 2>/dev/null || true
  if [ "$WORKING_PORT" = "8081" ]; then
    exit 0
  fi
  warn "Port 8081 indisponible — secours actif sur :${WORKING_PORT}"
  exit 0
fi

err "Aucun port 8081/8082/8083 ne répond"

echo ""
echo "==> Pile d'urgence (sans sudo)…"
if start_emergency_stack; then
  ok "Réparé — http://localhost:8083 (site + API)"
  echo "  API : http://localhost:8083/api/v1/"
  echo "  Admin : http://localhost:8083/admin/"
else
  err "Échec pile d'urgence"
fi

echo ""
echo "==> Réparation complète 8081 (sudo — supprime conteneurs root bloqués)…"
if sudo -n true 2>/dev/null; then
  sudo ./scripts/fix-docker-network.sh && ok "Stack compose restaurée sur :8081" || err "fix-docker-network a échoué"
else
  warn "Exécutez dans un terminal pour restaurer le port 8081 :"
  echo ""
  echo "    sudo ./scripts/fix-docker-network.sh"
  echo ""
  echo "  Utilisez en attendant : http://localhost:8083"
fi
