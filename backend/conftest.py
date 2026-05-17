import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'apps'))

import pytest


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    """Allow DB access in tests."""
    pass
