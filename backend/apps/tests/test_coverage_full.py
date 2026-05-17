"""Tests pour couverture 100 % du code applicatif."""
from datetime import date, timedelta
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.contrib.gis.geos import Point, Polygon
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestAccountsCoverage:
    def test_is_agent_property(self, agent_user):
        assert agent_user.is_agent is True
        assert agent_user.is_administrator is False

    def test_is_administrator(self, admin_user):
        assert admin_user.is_administrator is True

    def test_logout_view(self, auth_client):
        assert auth_client.post('/api/v1/auth/logout/').status_code == 200


@pytest.mark.django_db
class TestEducationCoverage:
    def test_all_badges(self, agent_user):
        from education.models import QuizSession, UserBadge, UserQuizProfile
        from education.services import award_badges, weekly_leaderboard

        profile, _ = UserQuizProfile.objects.get_or_create(user=agent_user)
        profile.total_score = 350
        profile.difficult_sessions_passed = 3
        profile.nasa_questions_total = 5
        profile.nasa_questions_correct = 5
        profile.save()
        QuizSession.objects.create(
            user=agent_user, difficulty='difficile', score=50,
            questions_answered=5, completed=True,
        )
        earned = award_badges(agent_user)
        assert UserBadge.objects.filter(user=agent_user).count() >= 1

        QuizSession.objects.create(
            user=agent_user, difficulty='facile', score=80,
            started_at=timezone.now(), completed=True,
        )
        board = weekly_leaderboard(5)
        assert isinstance(board, list)

    def test_quiz_errors(self, auth_client):
        r = auth_client.post('/api/v1/education/quiz/99999/answer/', {
            'question_id': 1, 'selected_index': 0,
        }, format='json')
        assert r.status_code == 404

    def test_quiz_finish_completed_session(self, auth_client, agent_user):
        from education.models import QuizSession
        s = QuizSession.objects.create(
            user=agent_user, difficulty='difficile', score=40,
            questions_answered=3, completed=True,
        )
        r = auth_client.post(f'/api/v1/education/quiz/{s.id}/finish/', {}, format='json')
        assert r.status_code == 400

    def test_quiz_mixte_and_nasa_answer(self, auth_client, db):
        from education.models import QuizQuestion
        QuizQuestion.objects.create(
            text='NASA?', difficulty='facile', choices=['A', 'B', 'C', 'D'],
            correct_index=0, explanation='E', points=5, is_nasa_topic=True,
        )
        QuizQuestion.objects.create(
            text='Sol?', difficulty='moyen', choices=['A', 'B', 'C', 'D'],
            correct_index=1, explanation='E', points=10,
        )
        start = auth_client.post('/api/v1/education/quiz/start/', {
            'difficulty': 'mixte', 'count': 2,
        }, format='json')
        sid = start.json()['session_id']
        q = start.json()['questions'][0]
        auth_client.post(f'/api/v1/education/quiz/{sid}/answer/', {
            'question_id': q['id'], 'selected_index': 0,
        }, format='json')
        fin = auth_client.post(f'/api/v1/education/quiz/{sid}/finish/', {}, format='json')
        assert fin.status_code == 200
        auth_client.get('/api/v1/education/quiz/badges/')


@pytest.mark.django_db
class TestNasaCoverage:
    def test_admin_ingest_and_enrich(self, admin_user, api_client):
        token = RefreshToken.for_user(admin_user).access_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        r = api_client.post('/api/v1/nasa/ingest/', {'enrich_points': False}, format='json')
        assert r.status_code == 200
        r2 = api_client.post('/api/v1/nasa/enrich-points/', {'limit': 10}, format='json')
        assert r2.status_code == 200

    def test_tile_png(self, api_client):
        r = api_client.get('/api/v1/nasa/tiles/MOD13Q1/2026-01-01/0/0/0.png')
        assert r.status_code == 200
        assert r['Content-Type'] == 'image/png'

    @patch('nasa.earthdata.earthaccess')
    def test_earthdata_login_success(self, mock_ea, settings):
        settings.NASA_EARTHDATA_USERNAME = 'u'
        settings.NASA_EARTHDATA_PASSWORD = 'p'
        mock_ea.login.return_value = True
        from nasa.earthdata import login, search_and_download
        assert login() is True

    @patch('nasa.earthdata.earthaccess')
    def test_earthdata_download(self, mock_ea, settings, tmp_path):
        settings.NASA_EARTHDATA_USERNAME = 'u'
        settings.NASA_EARTHDATA_PASSWORD = 'p'
        settings.NASA_CACHE_DIR = tmp_path
        mock_ea.login.return_value = True
        mock_ea.search_data.return_value = [{'id': 1}]
        mock_ea.download.return_value = [str(tmp_path / 'f.nc')]
        from nasa.earthdata import search_and_download
        files = search_and_download(
            'MOD13Q1', '061', (0.9, 6.0, 1.8, 6.8),
            ('2025-01-01', '2025-01-02'),
        )
        assert len(files) == 1

    def test_stac_search_exception(self):
        with patch('nasa.stac_client.Client') as mock_client:
            mock_client.open.side_effect = Exception('STAC down')
            from nasa.stac_client import search_granules
            assert search_granules('MOD13Q1', date.today(), date.today(), (0.9, 6, 1.8, 6.8)) == []

    @patch('nasa.raster_utils.rasterio')
    def test_raster_extract(self, mock_rio, tmp_path):
        from nasa.raster_utils import extract_point_value, clip_raster_to_bbox
        p = tmp_path / 't.tif'
        p.write_bytes(b'x')
        src = MagicMock()
        src.nodata = -999
        src.read.return_value = [[0.42]]
        src.index.return_value = (0, 0)
        mock_rio.open.return_value.__enter__.return_value = src
        assert extract_point_value(str(p), 1.2, 6.3) == 0.42
        assert clip_raster_to_bbox(str(p), tmp_path / 'out.tif', (0.9, 6, 1.8, 6.8)) is None

    def test_ingest_with_download_mock(self, settings, tmp_path):
        settings.NASA_CACHE_DIR = tmp_path
        settings.NASA_EARTHDATA_USERNAME = 'u'
        with patch('nasa.ingestion.search_and_download', return_value=[]):
            from nasa.ingestion import enrich_soil_points_from_rasters, ingest_product
            ingest_product('GPM', 'gpm', days_back=2)
            from soils.models import SoilPoint
            SoilPoint.objects.create(
                location=Point(1.2, 6.3, srid=4326), ph=6, humidity_pct=30,
                soil_type='limoneux', collected_at='2025-01-01', is_validated=True,
            )
            assert enrich_soil_points_from_rasters(limit=5) >= 0


@pytest.mark.django_db
class TestMlCoverage:
    def test_train_admin_xgboost(self, admin_user, api_client):
        token = RefreshToken.for_user(admin_user).access_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        with patch('ml_predict.pipeline.train_and_save', return_value={'f1_macro': 0.8}):
            r = api_client.post('/api/v1/ml/train/', {'algorithm': 'XGBoost'}, format='json')
        assert r.status_code == 201

    def test_pipeline_xgboost_and_synthetic(self):
        from ml_predict.pipeline import _synthetic_augment, train_and_save
        import pandas as pd
        df = _synthetic_augment(pd.DataFrame(), target=30)
        assert len(df) == 30
        with patch('ml_predict.pipeline.build_training_dataframe') as m:
            m.return_value = pd.DataFrame([{
                'ph': 6, 'humidity_pct': 30, 'soil_type': 'limoneux', 'slope_pct': 3,
                'ndvi_3m_avg': 0.4, 'smap_moisture_avg': 0.2, 'temperature': 28,
                'elevation_m': 50, 'season': 'seche', 'fertility_class': 'moyenne',
            }] * 40)
            metrics = train_and_save(algorithm='XGBoost')
        assert 'f1_macro' in metrics

    def test_celery_tasks(self):
        from ml_predict.tasks import check_retrain_fertility_model
        from nasa.tasks import ingest_all_nasa_layers
        with patch('ml_predict.tasks.train_and_save', return_value={'ok': True}):
            check_retrain_fertility_model()
        with patch('nasa.tasks.ingest_all', return_value={}):
            ingest_all_nasa_layers()


@pytest.mark.django_db
class TestSoilsCoverage:
    def test_str_methods(self, sample_soil_point, sample_zone):
        assert 'Sol #' in str(sample_soil_point)
        assert sample_zone.code in str(sample_zone)

    def test_import_geojson(self, auth_client):
        import json
        from django.core.files.uploadedfile import SimpleUploadedFile
        geojson = {
            'features': [{
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [1.22, 6.32]},
                'properties': {
                    'ph': 6.1, 'humidity_pct': 28, 'soil_type': 'sableux',
                    'collected_at': '2025-08-01',
                },
            }],
        }
        f = SimpleUploadedFile('t.geojson', json.dumps(geojson).encode(), content_type='application/json')
        r = auth_client.post('/api/v1/points/import_data/', {'file': f}, format='multipart')
        assert r.status_code == 200
        assert r.json()['created'] == 1

    def test_import_errors(self, auth_client):
        r = auth_client.post('/api/v1/points/import_data/', {}, format='multipart')
        assert r.status_code == 400
        from django.core.files.uploadedfile import SimpleUploadedFile
        f = SimpleUploadedFile('t.csv', b'a,b', content_type='text/csv')
        r2 = auth_client.post('/api/v1/points/import_data/', {'file': f}, format='multipart')
        assert r2.status_code == 400

    def test_agent_permission_denied(self, api_client):
        from django.contrib.auth import get_user_model
        u = get_user_model().objects.create_user('pub', password='x', role='public')
        from rest_framework_simplejwt.tokens import RefreshToken
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(u).access_token}')
        assert api_client.post('/api/v1/points/import_data/', {}, format='multipart').status_code == 403

    def test_seed_command(self):
        out = StringIO()
        call_command('seed_demo_data', stdout=out)
        assert 'ignoré' in out.getvalue().lower() or 'complete' in out.getvalue().lower()

    def test_train_command(self):
        out = StringIO()
        call_command('train_fertility_model', stdout=out)

    def test_ingest_nasa_command(self):
        out = StringIO()
        call_command('ingest_nasa', '--enrich-only', stdout=out)


@pytest.mark.django_db
class TestSpatialCoverage:
    def test_services_full(self, sample_soil_point, sample_zone):
        from spatial import services
        import json
        poly = {
            'type': 'Polygon',
            'coordinates': [[[1.05, 6.15], [1.45, 6.15], [1.45, 6.45], [1.05, 6.45], [1.05, 6.15]]],
        }
        services.intersection_zones(json.dumps(poly))
        buf = services.buffer_geometry(json.dumps({'type': 'Point', 'coordinates': [1.2, 6.3]}), 200)
        assert buf
        stats = services.spatial_statistics_by_zone()
        assert 'by_canton' in stats
        sample_soil_point.smap_moisture_avg = 0.2
        sample_soil_point.humidity_pct = 25
        sample_soil_point.save()
        for _ in range(15):
            from soils.models import SoilPoint
            SoilPoint.objects.create(
                location=Point(1.2 + _ * 0.01, 6.3, srid=4326),
                ph=6, humidity_pct=20 + _, soil_type='limoneux',
                collected_at='2025-01-01', is_validated=True,
                smap_moisture_avg=0.18,
            )
        services.smap_correlation()
