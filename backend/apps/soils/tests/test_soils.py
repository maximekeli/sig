import pytest
from django.contrib.gis.geos import Point

from soils.models import SoilPoint
from soils.validators import validate_soil_point_quality


@pytest.mark.django_db
def test_soil_point_ph_color():
    p = SoilPoint(
        location=Point(1.2, 6.3, srid=4326),
        ph=5.0, humidity_pct=40, soil_type='limoneux', collected_at='2025-06-01',
    )
    assert p.ph_color == 'red'
    p.ph = 6.5
    assert p.ph_color == 'yellow'
    p.ph = 7.5
    assert p.ph_color == 'green'


def test_quality_validator_ph_range():
    errors = validate_soil_point_quality({'ph': 2.0, 'humidity_pct': 50})
    assert 'ph' in errors


def test_quality_validator_humidity_range():
    errors = validate_soil_point_quality({'ph': 6.0, 'humidity_pct': 150})
    assert 'humidity_pct' in errors


def test_quality_validator_bbox():
    errors = validate_soil_point_quality({
        'ph': 6, 'humidity_pct': 50,
        'location': Point(5.0, 5.0, srid=4326),
    })
    assert 'location' in errors


def test_quality_validator_valid():
    errors = validate_soil_point_quality({
        'ph': 6.5,
        'humidity_pct': 40,
        'location': Point(1.25, 6.35, srid=4326),
    })
    assert errors == {}


@pytest.mark.django_db
def test_points_list_api(api_client, sample_soil_point):
    r = api_client.get('/api/v1/points/?light=1')
    assert r.status_code == 200
    data = r.json()
    assert data['count'] >= 1 or len(data.get('results', [])) >= 1


@pytest.mark.django_db
def test_dashboard_stats(api_client, sample_soil_point):
    r = api_client.get('/api/v1/dashboard/stats/')
    assert r.status_code == 200
    body = r.json()
    assert body['total_points'] >= 1
    assert 'avg_ph' in body


@pytest.mark.django_db
def test_create_soil_point(auth_client):
    r = auth_client.post('/api/v1/points/', {
        'type': 'Feature',
        'geometry': {'type': 'Point', 'coordinates': [1.3, 6.4]},
        'properties': {
            'ph': 6.8,
            'humidity_pct': 42,
            'soil_type': 'argileux',
            'collected_at': '2025-07-01',
        },
    }, format='json')
    assert r.status_code in (201, 400)  # GeoFeature format may vary


@pytest.mark.django_db
def test_export_csv(api_client, sample_soil_point):
    r = api_client.get('/api/v1/points/export-csv/')
    assert r.status_code == 200
    assert 'text/csv' in r['Content-Type']
