#!/usr/bin/env bash
# Répare le réseau Docker Compose quand web/db ne communiquent plus (timeout 5432, 502 nginx).
set -uo pipefail
cd "$(dirname "$0")/.."

dc() {
  if docker compose "$@" 2>/dev/null; then return 0; fi
  sudo docker compose "$@"
}

force_kill_container() {
  local cid="$1"
  local name pid
  name=$(docker inspect -f '{{.Name}}' "$cid" 2>/dev/null | sed 's#^/##' || echo "$cid")
  pid=$(docker inspect -f '{{.State.Pid}}' "$cid" 2>/dev/null || echo 0)
  echo "  force kill: $name ($cid) PID=$pid"
  if [ -n "$pid" ] && [ "$pid" != "0" ] && [ "$pid" != "<no value>" ]; then
    sudo kill -9 "$pid" 2>/dev/null || true
  fi
  sudo docker rm -f "$cid" 2>/dev/null || docker rm -f "$cid" 2>/dev/null || true
}

echo "==> Arrêt forcé de tous les conteneurs du projet…"
mapfile -t CIDS < <(docker ps -aq --filter "name=dusol_projet" 2>/dev/null; docker ps -aq --filter "name=dusol_sig" 2>/dev/null)
if [ "${#CIDS[@]}" -gt 0 ]; then
  for cid in "${CIDS[@]}"; do
    [ -n "$cid" ] && force_kill_container "$cid"
  done
fi

echo "==> docker compose down (volumes conservés)…"
dc down --remove-orphans || true

echo "==> Suppression du réseau bridge…"
docker network rm dusol_projet_default 2>/dev/null \
  || sudo docker network rm dusol_projet_default 2>/dev/null \
  || true

echo "==> Redémarrage complet…"
dc up -d --no-build --remove-orphans

echo "==> Attente santé db/redis…"
for i in $(seq 1 24); do
  if dc exec -T db pg_isready -U sig_sols >/dev/null 2>&1; then
    echo "  db ready"
    break
  fi
  sleep 2
done
sleep 3

echo "==> Test connectivité web -> db…"
if ! dc exec -T web python - <<'PY'
import socket
s = socket.socket()
s.settimeout(5)
code = s.connect_ex(("db", 5432))
print("connect_ex:", code)
raise SystemExit(0 if code == 0 else 1)
PY
then
  echo "ERREUR: web ne joint toujours pas db. Relancez: sudo systemctl restart docker && sudo ./scripts/fix-docker-network.sh"
  exit 1
fi

echo "==> Test HTTP…"
curl -sf http://localhost:8081/health/ && echo
dc exec -T web python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['ENGINE'])"
echo "OK — PostGIS opérationnel."
