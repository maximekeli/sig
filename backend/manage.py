#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
# Projet Django (config.*) + apps métier (accounts.*, soils.*, …)
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / 'apps'))


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
