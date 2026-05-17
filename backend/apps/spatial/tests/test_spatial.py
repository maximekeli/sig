import pytest
from django.contrib.gis.geos import Point

from soils.models import SoilPoint
from spatial import services


@pytest.mark.django_db
def test_proximity_search():
    SoilPoint.objects.create(
        location=Point(1.25, 6.35, srid=4326),
        ph=6.0, humidity_pct=30, soil_type='limoneux',
        collected_at='2025-03-01', is_validated=True,
    )
    results = services.proximity_search(1.25, 6.35, 5000)
    assert len(results) >= 1
