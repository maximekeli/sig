"""Pytest fixtures — PYTHONPATH: backend/apps (see pytest.ini)."""
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault('DJANGO_TEST', '1')
os.environ.setdefault('CELERY_TASK_ALWAYS_EAGER', '1')

_APPS = Path(__file__).resolve().parent / 'apps'
if str(_APPS) not in sys.path:
    sys.path.insert(0, str(_APPS))


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def agent_user(db):
    from accounts.models import User
    user = User.objects.create_user(
        username='test_agent',
        password='testpass123',
        role=User.Role.AGENT,
        is_staff=True,
    )
    return user


@pytest.fixture
def admin_user(db):
    from accounts.models import User
    return User.objects.create_superuser(
        username='test_admin',
        password='testpass123',
        role=User.Role.ADMIN,
    )


@pytest.fixture
def admin_client(api_client, admin_user):
    from rest_framework_simplejwt.tokens import RefreshToken
    token = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return api_client


@pytest.fixture
def auth_client(api_client, agent_user):
    from rest_framework_simplejwt.tokens import RefreshToken
    token = RefreshToken.for_user(agent_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return api_client


@pytest.fixture
def sample_soil_point(db):
    from datetime import date
    from django.contrib.gis.geos import Point
    from soils.models import SoilPoint
    return SoilPoint.objects.create(
        location=Point(1.25, 6.35, srid=4326),
        ph=6.2,
        humidity_pct=35.0,
        soil_type='limoneux',
        fertility_class='moyenne',
        fertility_score=0.55,
        ndvi_3m_avg=0.45,
        smap_moisture_avg=0.22,
        slope_pct=3.0,
        collected_at=date(2025, 6, 1),
        is_validated=True,
        source='test',
    )


@pytest.fixture
def sample_zone(db):
    from django.contrib.gis.geos import MultiPolygon, Polygon
    from soils.models import AdministrativeZone
    poly = Polygon((
        (1.0, 6.1), (1.5, 6.1), (1.5, 6.5), (1.0, 6.5), (1.0, 6.1),
    ))
    return AdministrativeZone.objects.create(
        name='Canton Test',
        code='TEST-01',
        zone_type='canton',
        geometry=MultiPolygon(poly),
    )
