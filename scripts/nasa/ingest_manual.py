#!/usr/bin/env python3
"""Manual NASA ingestion — run inside web container:
  docker compose exec web python /app/../scripts/nasa/ingest_manual.py
Or from project root:
  docker compose exec web python scripts/nasa/ingest_manual.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / 'backend'
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / 'apps'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django  # noqa: E402

django.setup()

from nasa.ingestion import ingest_all  # noqa: E402

if __name__ == '__main__':
    print(ingest_all())
