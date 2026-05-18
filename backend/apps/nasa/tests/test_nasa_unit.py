"""Tests unitaires NASA — mocks, pas d'appel réseau obligatoire."""
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from nasa.earthdata import EARTHDATA_PRODUCTS, login, search_and_download
from nasa.ingestion import ingest_product
from nasa.models import NasaLayerCatalog


@pytest.mark.django_db
class TestNasaEarthdataUnit:
    def test_login_false_without_credentials(self, settings):
        settings.NASA_EARTHDATA_USERNAME = ''
        settings.NASA_EARTHDATA_PASSWORD = ''
        settings.NASA_EARTHDATA_TOKEN = ''
        assert login() is False

    @override_settings(
        NASA_EARTHDATA_USERNAME='kelidzidula',
        NASA_EARTHDATA_PASSWORD='',
        NASA_EARTHDATA_TOKEN='fake-jwt-token',
    )
    @patch('earthaccess.login', return_value=MagicMock())
    def test_login_with_jwt_token(self, mock_login):
        assert login() is True
        mock_login.assert_called_once_with(strategy='environment')

    @override_settings(
        NASA_EARTHDATA_USERNAME='',
        NASA_EARTHDATA_PASSWORD='',
        NASA_EARTHDATA_TOKEN='token-only',
    )
    @patch('earthaccess.login', return_value=MagicMock())
    def test_login_token_only_no_username(self, mock_login):
        import os
        os.environ.pop('EARTHDATA_TOKEN', None)
        assert login() is True
        assert os.environ['EARTHDATA_TOKEN'] == 'token-only'

    @override_settings(
        NASA_EARTHDATA_USERNAME='user',
        NASA_EARTHDATA_PASSWORD='pass',
        NASA_EARTHDATA_TOKEN='',
    )
    @patch('earthaccess.login', return_value=None)
    def test_login_failure_returns_false(self, mock_login):
        assert login() is False

    @override_settings(NASA_EARTHDATA_USERNAME='', NASA_EARTHDATA_TOKEN='')
    def test_search_and_download_skips_without_auth(self):
        files = search_and_download(
            'MOD13Q1', '061', (0.9, 6.0, 1.8, 6.8), ('2025-01-01', '2025-01-31'),
        )
        assert files == []

    @override_settings(
        NASA_EARTHDATA_USERNAME='user',
        NASA_EARTHDATA_TOKEN='tok',
    )
    @patch('nasa.earthdata.login', return_value=True)
    @patch('earthaccess.download', return_value=['/cache/a.tif'])
    @patch('earthaccess.search_data', return_value=[{'id': 'g1'}])
    def test_search_and_download_success(self, mock_search, mock_dl, mock_login):
        files = search_and_download(
            'MOD13Q1', '061', (0.9, 6.0, 1.8, 6.8), ('2025-01-01', '2025-01-31'), count=1,
        )
        assert files == ['/cache/a.tif']
        mock_search.assert_called_once()

    def test_earthdata_products_mapping(self):
        assert 'MOD13Q1' in EARTHDATA_PRODUCTS
        assert EARTHDATA_PRODUCTS['SMAP'][0] == 'SPL3SMP_E'


@pytest.mark.django_db
class TestNasaIngestionUnit:
    @override_settings(NASA_EARTHDATA_USERNAME='', NASA_EARTHDATA_PASSWORD='', NASA_EARTHDATA_TOKEN='')
    @patch('nasa.ingestion.search_and_download', return_value=[])
    @patch('nasa.ingestion.search_granules', return_value=[])
    def test_ingest_product_demo_mode_without_download(self, mock_stac, mock_dl):
        n = ingest_product('MOD13Q1', 'MODIS NDVI', days_back=3)
        assert n >= 1
        layer = NasaLayerCatalog.objects.filter(product='MOD13Q1').first()
        assert layer is not None
        assert layer.metadata.get('demo_mode') is True
        assert layer.metadata.get('source') == 'NASA Earthdata'

    @override_settings(NASA_EARTHDATA_USERNAME='user', NASA_EARTHDATA_TOKEN='tok')
    @patch('nasa.ingestion.search_and_download', return_value=['/tmp/fake.tif'])
    @patch('nasa.ingestion.search_granules', return_value=[{'id': 'stac-1'}])
    @patch('nasa.raster_utils.clip_raster_to_bbox', return_value='/tmp/clipped.tif')
    def test_ingest_product_not_demo_when_downloaded(
        self, mock_clip, mock_stac, mock_dl,
    ):
        n = ingest_product('MOD13Q1', 'MODIS NDVI', days_back=2)
        assert n >= 1
        layer = NasaLayerCatalog.objects.filter(product='MOD13Q1').latest('acquisition_date')
        assert layer.metadata.get('demo_mode') is False
        assert 'downloaded_files' in layer.metadata


@pytest.mark.django_db
class TestNasaStacUnit:
    @patch('pystac_client.Client.open')
    def test_stac_search_returns_items(self, mock_open):
        item = MagicMock()
        item.id = 'granule-1'
        item.datetime = None
        item.assets = {'data': MagicMock()}
        item.bbox = [1, 6, 1.1, 6.1]
        item.self_href = 'http://example.com/item'

        mock_client = MagicMock()
        mock_client.search.return_value.items.return_value = [item]
        mock_open.return_value = mock_client

        from nasa.stac_client import search_granules
        results = search_granules(
            'MOD13Q1', date(2025, 1, 1), date(2025, 1, 31),
            (0.9, 6.0, 1.8, 6.8), limit=5,
        )
        assert len(results) == 1
        assert results[0]['id'] == 'granule-1'

    def test_stac_unknown_product_returns_empty(self):
        from nasa.stac_client import search_granules
        assert search_granules(
            'UNKNOWN', date(2025, 1, 1), date(2025, 1, 31),
            (0.9, 6.0, 1.8, 6.8),
        ) == []


@pytest.mark.django_db
class TestNasaApiUnit:
    def test_layers_list(self, api_client):
        from django.contrib.gis.geos import Polygon
        NasaLayerCatalog.objects.create(
            product='MOD13Q1',
            layer_name='test_layer',
            acquisition_date=date.today(),
            bbox=Polygon.from_bbox((0.9, 6.0, 1.8, 6.8)),
        )
        r = api_client.get('/api/v1/nasa/layers/')
        assert r.status_code == 200

    def test_catalog_summary_structure(self, api_client):
        r = api_client.get('/api/v1/nasa/catalog/summary/')
        assert r.status_code == 200
        data = r.json()
        assert 'total_layers' in data
        assert 'by_product' in data
        assert 'products' in data
