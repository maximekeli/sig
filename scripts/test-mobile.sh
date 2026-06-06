#!/usr/bin/env bash
# Tests application mobile Flutter
set -euo pipefail
cd "$(dirname "$0")/../mobile"

echo "==> Tests unitaires Flutter (sans intégration API)…"
flutter test --exclude-tags integration

echo ""
echo "==> Tests intégration API (backend requis sur :8081)…"
if curl -sf --max-time 5 http://localhost:8081/health/ >/dev/null 2>&1; then
  flutter test --tags integration
  echo "OK — tests intégration passés."
else
  echo "AVERTISSEMENT: backend indisponible — tests intégration ignorés."
  echo "  Lancez: cd .. && docker compose up -d && sudo ./scripts/fix-docker-network.sh"
fi

echo ""
echo "OK — tests mobile terminés."
