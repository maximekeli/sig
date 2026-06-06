#!/usr/bin/env bash
# Tests de liaison backend ↔ site web ↔ mobile
set -uo pipefail
cd "$(dirname "$0")/.."

PASS=0
FAIL=0
SKIP=0

ok()   { echo "  ✓ $1"; PASS=$((PASS + 1)); }
ko()   { echo "  ✗ $1"; FAIL=$((FAIL + 1)); }
skip() { echo "  ⊘ $1"; SKIP=$((SKIP + 1)); }

echo "═══════════════════════════════════════════════════════════"
echo " SIG Sols Togo — Tests de liaison backend / web / mobile"
echo "═══════════════════════════════════════════════════════════"

echo ""
echo "==> 1/4 Backend — liaison API (pytest, sans serveur live)…"
if docker compose run --rm --no-deps --entrypoint "" web \
    pytest apps/tests/test_api_linkage.py apps/tests/test_integration.py -q --tb=line 2>&1 | tail -5; then
  ok "Backend liaison API"
else
  ko "Backend liaison API"
fi

echo ""
echo "==> 2/4 Frontend — tests unitaires JS…"
if (cd frontend && npm test --silent 2>&1 | tail -3); then
  ok "Frontend unitaires"
else
  ko "Frontend unitaires"
fi

echo ""
echo "==> 3/4 Mobile — tests unitaires Flutter…"
if (cd mobile && flutter test --exclude-tags integration 2>&1 | tail -2); then
  ok "Mobile unitaires"
else
  ko "Mobile unitaires"
fi

echo ""
echo "==> 4/4 Live HTTP — backend Docker…"
BASE=""
API=""
for port in 8081 8082 8083; do
  if curl -sf --max-time 8 "http://127.0.0.1:${port}/health/" >/dev/null 2>&1; then
    BASE="http://localhost:${port}"
    API="$BASE/api/v1"
    ok "Backend live sur :${port}"
    break
  fi
done

if [ -z "$BASE" ]; then
  skip "Backend live indisponible — lancez: make repair-docker ou sudo ./scripts/fix-docker-network.sh"
  echo ""
  echo "  Cause fréquente : conteneur web orphelin bloqué."
  docker ps -a --filter name=web --format '  - {{.Names}} ({{.Status}})' 2>/dev/null || true
else
  if curl -sf --max-time 8 "$BASE/health/?detail=1" | grep -q '"database":"ok"'; then
    ok "PostGIS accessible"
  else
    ko "PostGIS health"
  fi

  TOKEN=$(curl -sf --max-time 10 -X POST "$API/auth/token/" \
    -H 'Content-Type: application/json' \
    -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin).get('access',''))" 2>/dev/null || true)

  if [ -n "$TOKEN" ]; then
    ok "Auth JWT admin"
    AUTH_H="Authorization: Bearer $TOKEN"

    for path in \
      "/points/?light=1" \
      "/dashboard/stats/" \
      "/weather/status/" \
      "/sentinel/status/" \
      "/assistant/status/" \
      "/nasa/catalog/summary/" \
      "/ml/metrics/" \
      "/spatial/smap-correlation/" \
      "/education/quiz/stats/" \
      "/videos/posts/?kind=video"; do
      if curl -sf --max-time 12 -H "$AUTH_H" "$API$path" >/dev/null 2>&1 \
         || curl -sf --max-time 12 "$API$path" >/dev/null 2>&1; then
        ok "GET $path"
      else
        ko "GET $path"
      fi
    done

    echo ""
    echo "  Mobile intégration Flutter…"
    if (cd mobile && flutter test --tags integration 2>&1 | tail -3); then
      ok "Mobile intégration live"
    else
      ko "Mobile intégration live"
    fi
  else
    ko "Auth JWT — seed_demo_data requis ?"
  fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo " Résultat : $PASS OK · $FAIL échec(s) · $SKIP ignoré(s)"
echo "═══════════════════════════════════════════════════════════"

[ "$FAIL" -eq 0 ]
