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


def test_quality_validator_bbox():
    errors = validate_soil_point_quality({
        'ph': 6, 'humidity_pct': 50,
        'location': Point(5.0, 5.0, srid=4326),
    })
    assert 'location' in errors
