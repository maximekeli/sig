#!/usr/bin/env python3
"""Manual NASA ingestion — run inside web container."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend/apps'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from nasa.ingestion import ingest_all

if __name__ == '__main__':
    print(ingest_all())
