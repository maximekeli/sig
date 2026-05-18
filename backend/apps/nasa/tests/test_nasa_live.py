"""
Tests d'intégration NASA — appels réseau réels.

Exécution :
  docker compose exec web pytest apps/nasa/tests/test_nasa_live.py -v -s

Nécessite dans .env : NASA_EARTHDATA_TOKEN ou NASA_EARTHDATA_USERNAME/PASSWORD
"""
import os
from datetime import date, timedelta

import pytest
from django.conf import settings

pytestmark = pytest.mark.nasa_live


def _has_nasa_credentials():
    return bool(
        os.environ.get('NASA_EARTHDATA_TOKEN')
        or settings.NASA_EARTHDATA_TOKEN
        or os.environ.get('NASA_EARTHDATA_USERNAME')
        or settings.NASA_EARTHDATA_USERNAME
    )


skip_no_creds = pytest.mark.skipif(
    not _has_nasa_credentials(),
    reason='NASA_EARTHDATA_TOKEN ou NASA_EARTHDATA_USERNAME absent dans .env',
)


@pytest.mark.django_db
@skip_no_creds
class TestNasaLiveEarthdata:
    def test_live_login(self):
        from nasa.earthdata import login
        assert login() is True, (
            'Connexion NASA échouée — vérifiez NASA_EARTHDATA_TOKEN dans .env '
            '(token expiré ? régénérez sur https://urs.earthdata.nasa.gov/)'
        )

    def test_live_search_granules_mod13(self):
        """Recherche CMR sans téléchargement (léger)."""
        from nasa.earthdata import login, EARTHDATA_PRODUCTS
        import earthaccess

        assert login()
        short_name, version = EARTHDATA_PRODUCTS['MOD13Q1']
        end = date.today()
        start = end - timedelta(days=60)
        bbox = settings.REGION_MARITIME_BBOX
        results = earthaccess.search_data(
            short_name=short_name,
            version=version,
            bounding_box=bbox,
            temporal=(start.isoformat(), end.isoformat()),
            count=3,
        )
        assert results is not None
        assert len(results) >= 1, 'Aucun granule MOD13Q1 trouvé pour la zone Maritime'


@pytest.mark.django_db
class TestNasaLiveStac:
    """STAC CMR — catalogue public, sans token."""

    def test_live_stac_mod13_maritime(self):
        from nasa.stac_client import search_granules
        end = date.today()
        start = end - timedelta(days=90)
        bbox = tuple(settings.REGION_MARITIME_BBOX)
        results = search_granules('MOD13Q1', start, end, bbox, limit=5)
        assert isinstance(results, list)
        # STAC peut retourner [] si collection ID change — on vérifie au moins pas d'exception
        if results:
            assert 'id' in results[0]
            assert 'datetime' in results[0]


@pytest.mark.django_db
@skip_no_creds
class TestNasaLiveIngestion:
    def test_live_ingest_one_product(self):
        from nasa.ingestion import ingest_product
        from nasa.models import NasaLayerCatalog

        before = NasaLayerCatalog.objects.filter(product='GPM').count()
        created = ingest_product('GPM', 'GPM precipitation', days_back=7)
        assert created >= 1
        assert NasaLayerCatalog.objects.filter(product='GPM').count() > before
        latest = NasaLayerCatalog.objects.filter(product='GPM').latest('acquisition_date')
        assert latest.metadata.get('source') == 'NASA Earthdata'
