from datetime import date

import pytest

from nasa.ingestion import ingest_product, ingest_all
from nasa.models import NasaLayerCatalog


@pytest.mark.django_db
def test_ingest_product_creates_catalog():
    n = ingest_product('MOD13Q1', 'MODIS NDVI', days_back=5)
    assert n >= 1
    assert NasaLayerCatalog.objects.filter(product='MOD13Q1').exists()


@pytest.mark.django_db
def test_ingest_all_products():
    totals = ingest_all()
    assert 'MOD13Q1' in totals
    assert NasaLayerCatalog.objects.count() >= 5


@pytest.mark.django_db
def test_nasa_layers_api(api_client):
    ingest_product('SMAP', 'SMAP', days_back=3)
    r = api_client.get('/api/v1/nasa/layers/')
    assert r.status_code == 200


@pytest.mark.django_db
def test_nasa_catalog_summary(api_client):
    ingest_product('GPM', 'GPM', days_back=2)
    r = api_client.get('/api/v1/nasa/catalog/summary/')
    assert r.status_code == 200
    assert 'total_layers' in r.json()


@pytest.mark.nasa_live
@pytest.mark.django_db
def test_stac_search_no_crash():
    """Réseau NASA STAC — exécuter avec: NASA_LIVE_TESTS=1 pytest -m nasa_live."""
    from nasa.stac_client import search_granules
    bbox = (0.9, 6.0, 1.8, 6.8)
    results = search_granules('MOD13Q1', date(2025, 1, 1), date(2025, 1, 31), bbox, limit=2)
    assert isinstance(results, list)


@pytest.mark.django_db
def test_earthdata_login_without_credentials(settings):
    settings.NASA_EARTHDATA_USERNAME = ''
    settings.NASA_EARTHDATA_PASSWORD = ''
    settings.NASA_EARTHDATA_TOKEN = ''
    from nasa.earthdata import login
    assert login() is False
