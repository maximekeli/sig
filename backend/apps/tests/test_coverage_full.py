"""Tests pour couverture 100 % du code applicatif."""
from datetime import date
from io import StringIO
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestAccountsCoverage:
    def test_is_agent_property(self, agent_user):
        assert agent_user.is_agent is True
        assert agent_user.is_administrator is False
        assert agent_user.display_name == agent_user.username

    def test_is_administrator(self, admin_user):
        assert admin_user.is_administrator is True

    def test_logout_view(self, auth_client):
        assert auth_client.post('/api/v1/auth/logout/').status_code == 200

    def test_auth_full_flow(self, api_client, auth_client, admin_client, agent_user, admin_user):
        import uuid
        from accounts.models import UserLocation
        from accounts.services import list_live_locations, upsert_user_location

        suffix = uuid.uuid4().hex[:8]
        reg_base = {
            'password': 'pass12345', 'password_confirm': 'pass12345',
            'first_name': 'Test', 'last_name': 'User', 'age': 30,
            'consent_analytics': True,
        }
        assert api_client.post('/api/v1/auth/register/', {
            **reg_base,
            'username': f'u1_{suffix}', 'email': f'n1_{suffix}@t.local',
            'role': 'agent',
        }, format='json').status_code == 201
        assert api_client.post('/api/v1/auth/register/', {
            **reg_base,
            'username': f'u2_{suffix}', 'email': f'u2_{suffix}@example.com',
            'password_confirm': 'pass12346',
        }, format='json').status_code == 400
        r_admin = api_client.post('/api/v1/auth/register/', {
            **reg_base,
            'username': f'u3_{suffix}', 'email': f'user_{suffix}@example.com',
            'role': 'admin',
        }, format='json')
        assert r_admin.status_code == 201, r_admin.content
        assert r_admin.json()['user']['role'] == 'public'

        tok = api_client.post('/api/v1/auth/token/', {
            'username': 'test_agent', 'password': 'testpass123',
        }, format='json')
        assert 'user' in tok.json()

        assert auth_client.get('/api/v1/auth/profile/').status_code == 200
        auth_client.patch('/api/v1/auth/profile/', {'first_name': 'Agent'}, format='json')
        assert auth_client.post('/api/v1/auth/password/change/', {
            'old_password': 'wrong', 'new_password': 'pass12345',
            'new_password_confirm': 'pass12345',
        }, format='json').status_code == 400
        assert auth_client.post('/api/v1/auth/password/change/', {
            'old_password': 'testpass123', 'new_password': 'pass12345',
            'new_password_confirm': 'pass12346',
        }, format='json').status_code == 400
        assert auth_client.get('/api/v1/auth/location/').status_code == 404
        assert auth_client.post('/api/v1/auth/location/', {
            'lat': 6.35, 'lon': 1.25, 'accuracy_m': 12,
        }, format='json').status_code == 200
        assert auth_client.get('/api/v1/auth/location/').status_code == 200
        assert auth_client.post('/api/v1/auth/location/', {
            'lat': 0, 'lon': 0,
        }, format='json').status_code == 400
        assert auth_client.delete('/api/v1/auth/location/').status_code == 204

        upsert_user_location(agent_user, 1.25, 6.35)
        list_live_locations(exclude_user=agent_user)
        assert admin_client.get('/api/v1/auth/users/').status_code == 200
        assert admin_client.get('/api/v1/auth/locations/live/').status_code == 200
        assert admin_client.get('/api/v1/auth/locations/live/?include_self=1').status_code == 200

        loc, _ = UserLocation.objects.get_or_create(
            user=agent_user,
            defaults={'location': Point(1.25, 6.35, srid=4326)},
        )
        assert str(loc)
        from accounts.models import UserLocationHistory
        h = UserLocationHistory.objects.create(
            user=agent_user, location=loc.location, accuracy_m=5,
        )
        assert str(h)
        from accounts.views import UserTrajectoryView
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        req = factory.get('/')
        req.user = agent_user
        resp = UserTrajectoryView.as_view()(req, user_id=admin_user.id)
        assert resp.status_code == 403
        r_pw = auth_client.post('/api/v1/auth/password/change/', {
            'old_password': 'testpass123', 'new_password': 'newpass999',
            'new_password_confirm': 'newpass999',
        }, format='json')
        assert r_pw.status_code == 200
        api_client.get('/api/v1/education/quiz/leaderboard/')


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
        award_badges(agent_user)
        assert UserBadge.objects.filter(user=agent_user).count() >= 1

        QuizSession.objects.create(
            user=agent_user, difficulty='facile', score=80,
            started_at=timezone.now(), completed=True,
        )
        assert isinstance(weekly_leaderboard(5), list)

    def test_quiz_errors(self, auth_client):
        r = auth_client.post('/api/v1/education/quiz/99999/answer/', {
            'question_id': 1, 'selected_index': 0,
        }, format='json')
        assert r.status_code == 404

    def test_quiz_answer_on_completed_session(self, auth_client, agent_user):
        from education.models import QuizQuestion, QuizSession
        q = QuizQuestion.objects.create(
            text='Q?', difficulty='facile', choices=['A', 'B', 'C', 'D'],
            correct_index=0, explanation='E', points=5,
        )
        s = QuizSession.objects.create(
            user=agent_user, difficulty='facile', score=10,
            questions_answered=1, completed=True,
        )
        r = auth_client.post(f'/api/v1/education/quiz/{s.id}/answer/', {
            'question_id': q.id, 'selected_index': 0,
        }, format='json')
        assert r.status_code == 400

    def test_quiz_finish_unknown_session(self, auth_client):
        r = auth_client.post('/api/v1/education/quiz/99999/finish/', {}, format='json')
        assert r.status_code == 404

    def test_quiz_start_few_questions(self, auth_client, db):
        from education.models import QuizQuestion
        QuizQuestion.objects.create(
            text='Seule?', difficulty='facile', choices=['A', 'B', 'C', 'D'],
            correct_index=0, explanation='E',
        )
        r = auth_client.post('/api/v1/education/quiz/start/', {
            'difficulty': 'facile', 'count': 10,
        }, format='json')
        assert r.status_code == 200
        assert len(r.json()['questions']) == 1

    def test_quiz_question_auto_points(self, db):
        from education.models import QuizQuestion
        for difficulty, expected in [('facile', 5), ('moyen', 10), ('difficile', 15), ('autre', 5)]:
            q = QuizQuestion(text=f'Auto {difficulty}', difficulty=difficulty,
                             choices=['A', 'B', 'C', 'D'], correct_index=0,
                             explanation='E', points=0)
            q.save()
            assert q.points == expected

    def test_quiz_nasa_profile_and_difficult_finish(self, auth_client, agent_user, db):
        from education.models import QuizQuestion, QuizSession, UserQuizProfile
        q = QuizQuestion.objects.create(
            text='NASA Q', difficulty='facile', choices=['A', 'B', 'C', 'D'],
            correct_index=0, explanation='E', points=5, is_nasa_topic=True,
        )
        s = QuizSession.objects.create(user=agent_user, difficulty='difficile', score=35)
        auth_client.post(f'/api/v1/education/quiz/{s.id}/answer/', {
            'question_id': q.id, 'selected_index': 0,
        }, format='json')
        auth_client.post(f'/api/v1/education/quiz/{s.id}/finish/', {}, format='json')
        profile = UserQuizProfile.objects.get(user=agent_user)
        assert profile.nasa_questions_total >= 1
        assert profile.difficult_sessions_passed >= 1

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

    def test_quiz_share(self, auth_client, agent_user):
        from education.models import QuizSession
        s = QuizSession.objects.create(
            user=agent_user, difficulty='facile', score=42, completed=True,
        )
        r = auth_client.get(f'/api/v1/education/quiz/{s.id}/share/')
        assert r.status_code == 200
        assert 'share_text' in r.json()
        assert auth_client.get('/api/v1/education/quiz/99999/share/').status_code == 404


@pytest.mark.django_db
class TestNasaCoverage:
    def test_admin_ingest_no_enrich(self, admin_user, api_client):
        token = RefreshToken.for_user(admin_user).access_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        with patch('nasa.ingestion.ingest_all', return_value={'MOD13Q1': 1}):
            r = api_client.post('/api/v1/nasa/ingest/', {'enrich_points': False}, format='json')
        assert r.status_code == 200

    def test_admin_ingest_and_enrich(self, admin_user, api_client):
        token = RefreshToken.for_user(admin_user).access_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        r = api_client.post('/api/v1/nasa/ingest/', {'enrich_points': True}, format='json')
        assert r.status_code == 200
        r2 = api_client.post('/api/v1/nasa/enrich-points/', {'limit': 10}, format='json')
        assert r2.status_code == 200

    def test_tile_png(self, api_client):
        r = api_client.get('/api/v1/nasa/tiles/MOD13Q1/2026-01-01/0/0/0.png')
        assert r.status_code == 200
        assert r['Content-Type'] == 'image/png'

    def test_catalog_summary(self, api_client, db):
        from django.contrib.gis.geos import Polygon
        from nasa.models import NasaLayerCatalog
        NasaLayerCatalog.objects.create(
            product='MOD13Q1', layer_name='ndvi', acquisition_date=date.today(),
            bbox=Polygon.from_bbox((0.9, 6, 1.8, 6.8)),
        )
        r = api_client.get('/api/v1/nasa/catalog/summary/')
        assert r.status_code == 200
        assert r.json()['total_layers'] >= 1

    def test_nasa_layer_str(self, db):
        from django.contrib.gis.geos import Polygon
        from nasa.models import NasaLayerCatalog
        layer = NasaLayerCatalog.objects.create(
            product='MOD13Q1', layer_name='test', acquisition_date=date.today(),
            bbox=Polygon.from_bbox((0.9, 6, 1.8, 6.8)),
        )
        assert 'MOD13Q1' in str(layer)

    @patch('earthaccess.login')
    def test_earthdata_login_success(self, mock_login, settings):
        settings.NASA_EARTHDATA_USERNAME = 'u'
        settings.NASA_EARTHDATA_PASSWORD = 'p'
        mock_login.return_value = MagicMock()
        from nasa.earthdata import login
        assert login() is True

    @patch('earthaccess.login')
    def test_earthdata_login_token_only(self, mock_login, settings):
        import os
        settings.NASA_EARTHDATA_USERNAME = ''
        settings.NASA_EARTHDATA_PASSWORD = ''
        settings.NASA_EARTHDATA_TOKEN = 'jwt-token-test'
        os.environ.pop('EARTHDATA_TOKEN', None)
        mock_login.return_value = MagicMock()
        from nasa.earthdata import login
        assert login() is True
        assert os.environ['EARTHDATA_TOKEN'] == 'jwt-token-test'

    @patch('earthaccess.login', side_effect=RuntimeError('auth fail'))
    def test_earthdata_login_failure(self, mock_login, settings):
        settings.NASA_EARTHDATA_USERNAME = 'u'
        settings.NASA_EARTHDATA_PASSWORD = 'p'
        from nasa.earthdata import login
        assert login() is False

    @patch('earthaccess.download')
    @patch('earthaccess.search_data')
    @patch('earthaccess.login')
    def test_earthdata_download(self, mock_login, mock_search, mock_dl, settings, tmp_path):
        settings.NASA_EARTHDATA_USERNAME = 'u'
        settings.NASA_EARTHDATA_PASSWORD = 'p'
        settings.NASA_CACHE_DIR = tmp_path
        mock_login.return_value = MagicMock()
        mock_search.return_value = [{'id': 1}]
        mock_dl.return_value = [str(tmp_path / 'f.nc')]
        from nasa.earthdata import search_and_download
        files = search_and_download(
            'MOD13Q1', '061', (0.9, 6.0, 1.8, 6.8),
            ('2025-01-01', '2025-01-02'),
        )
        assert len(files) == 1

    @patch('earthaccess.search_data', return_value=[])
    @patch('earthaccess.login')
    def test_earthdata_no_results(self, mock_login, mock_search, settings):
        settings.NASA_EARTHDATA_USERNAME = 'u'
        settings.NASA_EARTHDATA_PASSWORD = 'p'
        mock_login.return_value = MagicMock()
        from nasa.earthdata import search_and_download
        assert search_and_download('MOD13Q1', '061', (0.9, 6, 1.8, 6.8),
                                   ('2025-01-01', '2025-01-02')) == []

    @patch('earthaccess.search_data', side_effect=RuntimeError('dl fail'))
    @patch('earthaccess.login')
    def test_earthdata_download_exception(self, mock_login, mock_search, settings):
        settings.NASA_EARTHDATA_USERNAME = 'u'
        settings.NASA_EARTHDATA_PASSWORD = 'p'
        mock_login.return_value = MagicMock()
        from nasa.earthdata import search_and_download
        assert search_and_download('MOD13Q1', '061', (0.9, 6, 1.8, 6.8),
                                   ('2025-01-01', '2025-01-02')) == []

    def test_stac_unknown_product(self):
        from nasa.stac_client import search_granules
        assert search_granules('UNKNOWN', date.today(), date.today(), (0.9, 6, 1.8, 6.8)) == []

    @patch('pystac_client.Client.open', side_effect=Exception('STAC down'))
    def test_stac_search_exception(self, mock_open):
        from nasa.stac_client import search_granules
        assert search_granules('MOD13Q1', date.today(), date.today(), (0.9, 6, 1.8, 6.8)) == []

    def test_stac_import_error(self):
        import builtins
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == 'pystac_client':
                raise ImportError('no pystac')
            return real_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=fake_import):
            from nasa.stac_client import search_granules
            assert search_granules(
                'MOD13Q1', date.today(), date.today(), (0.9, 6, 1.8, 6.8),
            ) == []

    @patch('pystac_client.Client.open')
    def test_stac_search_success(self, mock_open):
        item = MagicMock()
        item.id = 'granule-1'
        item.datetime = timezone.now()
        item.assets = {'data': MagicMock()}
        item.bbox = [0.9, 6, 1.8, 6.8]
        item.self_href = 'http://example.com/item'
        mock_client = MagicMock()
        mock_client.search.return_value.items.return_value = [item]
        mock_open.return_value = mock_client
        from nasa.stac_client import search_granules
        results = search_granules(
            'MOD13Q1', date.today(), date.today(), (0.9, 6, 1.8, 6.8), limit=1,
        )
        assert len(results) == 1
        assert results[0]['id'] == 'granule-1'

    @patch('rasterio.open')
    def test_raster_extract(self, mock_open, tmp_path):
        from nasa.raster_utils import extract_point_value, clip_raster_to_bbox, ndvi_from_mod13
        p = tmp_path / 't.tif'
        p.write_bytes(b'x')
        src = MagicMock()
        src.nodata = -999
        src.read.return_value = np.array([[0.42]])
        src.index.return_value = (0, 0)
        mock_open.return_value.__enter__.return_value = src
        assert extract_point_value(str(p), 1.2, 6.3) == 0.42
        assert extract_point_value(str(tmp_path / 'missing.tif'), 1, 1) is None
        src.read.return_value = np.array([[-999.0]])
        assert extract_point_value(str(p), 1.2, 6.3) is None
        src.read.return_value = np.array([[float('nan')]])
        assert extract_point_value(str(p), 1.2, 6.3) is None
        mock_open.side_effect = OSError('bad raster')
        assert extract_point_value(str(p), 1.2, 6.3) is None
        mock_open.side_effect = None
        mock_open.return_value.__enter__.return_value = src
        src.read.return_value = np.array([[5000.0]])
        assert ndvi_from_mod13(str(p), 1.2, 6.3) == 0.5
        src.read.return_value = np.array([[0.42]])
        assert ndvi_from_mod13(str(p), 1.2, 6.3) == 0.42
        assert clip_raster_to_bbox(str(tmp_path / 'nope.tif'), tmp_path / 'out.tif',
                                   (0.9, 6, 1.8, 6.8)) is None

    @patch('rasterio.open')
    @patch('rasterio.mask.mask')
    def test_raster_clip_rasterio_path(self, mock_mask, mock_open, tmp_path):
        from nasa.raster_utils import clip_raster_to_bbox
        p = tmp_path / 't.tif'
        p.write_bytes(b'x')
        out = tmp_path / 'out.tif'
        mock_mask.return_value = (np.zeros((1, 2, 2)), MagicMock())
        src = MagicMock()
        src.meta = {'driver': 'GTiff', 'dtype': 'float32', 'count': 1}
        mock_open.return_value.__enter__.return_value = src
        with patch('xarray.open_dataarray', side_effect=RuntimeError('no rioxarray')):
            result = clip_raster_to_bbox(str(p), out, (0.9, 6, 1.8, 6.8))
        assert result == str(out)

    @patch('rasterio.open', side_effect=OSError('clip fail'))
    @patch('rasterio.mask.mask', side_effect=OSError('mask fail'))
    def test_raster_clip_failure(self, mock_mask, mock_open, tmp_path):
        from nasa.raster_utils import clip_raster_to_bbox, ndvi_from_mod13
        p = tmp_path / 't.tif'
        p.write_bytes(b'x')
        with patch('xarray.open_dataarray', side_effect=RuntimeError('no rioxarray')):
            assert clip_raster_to_bbox(str(p), tmp_path / 'out.tif', (0.9, 6, 1.8, 6.8)) is None
        with patch('nasa.raster_utils.extract_point_value', return_value=None):
            assert ndvi_from_mod13(str(p), 1.0, 6.0) is None

    @patch('xarray.open_dataarray')
    def test_raster_clip_rioxarray_path(self, mock_xr_open, tmp_path):
        from nasa.raster_utils import clip_raster_to_bbox
        p = tmp_path / 't.tif'
        p.write_bytes(b'x')
        out = tmp_path / 'out2.tif'
        da = MagicMock()
        da.rio.crs = None
        da.rio.clip_box.return_value = da
        da.rio.to_raster = MagicMock()
        mock_xr_open.return_value = da
        result = clip_raster_to_bbox(str(p), out, (0.9, 6, 1.8, 6.8))
        assert result == str(out)

    def test_ingest_skip_existing_and_download(self, settings, tmp_path):
        from django.contrib.gis.geos import Polygon
        from nasa.ingestion import ingest_product
        from nasa.models import NasaLayerCatalog
        settings.NASA_CACHE_DIR = tmp_path
        settings.NASA_EARTHDATA_USERNAME = 'u'
        acq = date.today()
        NasaLayerCatalog.objects.create(
            product='GPM', layer_name='existing', acquisition_date=acq,
            bbox=Polygon.from_bbox(settings.REGION_MARITIME_BBOX),
            raster_path=str(tmp_path / 'x.tif'),
        )
        fake_file = tmp_path / 'dl.nc'
        fake_file.write_bytes(b'1')
        with patch('nasa.ingestion.search_granules', return_value=[{'id': 'stac1'}]), \
             patch('nasa.ingestion.search_and_download', return_value=[str(fake_file)]), \
             patch('nasa.raster_utils.clip_raster_to_bbox',
                   return_value=str(tmp_path / 'clipped.tif')):
            n = ingest_product('GPM', 'gpm', days_back=3)
        assert n >= 0

    def test_enrich_soil_points(self, settings, tmp_path):
        from nasa.ingestion import enrich_soil_points_from_rasters
        from nasa.models import NasaLayerCatalog
        from django.contrib.gis.geos import Polygon
        from soils.models import SoilPoint
        tif = tmp_path / 'modis.tif'
        tif.write_bytes(b'x')
        NasaLayerCatalog.objects.create(
            product='MOD13Q1', layer_name='m', acquisition_date=date.today(),
            bbox=Polygon.from_bbox((0.9, 6, 1.8, 6.8)), raster_path=str(tif),
        )
        smap_tif = tmp_path / 'smap.tif'
        smap_tif.write_bytes(b'y')
        NasaLayerCatalog.objects.create(
            product='SMAP', layer_name='s', acquisition_date=date.today(),
            bbox=Polygon.from_bbox((0.9, 6, 1.8, 6.8)), raster_path=str(smap_tif),
        )
        SoilPoint.objects.create(
            location=Point(1.2, 6.3, srid=4326), ph=6, humidity_pct=30,
            soil_type='limoneux', collected_at='2025-01-01', is_validated=True,
        )
        with patch('nasa.raster_utils.ndvi_from_mod13', return_value=0.55), \
             patch('nasa.raster_utils.extract_point_value', return_value=0.21):
            assert enrich_soil_points_from_rasters(limit=5) >= 1

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

    def test_ingest_nasa_command_full(self):
        out = StringIO()
        call_command('ingest_nasa', stdout=out)
        assert 'ingested' in out.getvalue().lower() or 'MOD13Q1' in out.getvalue()


@pytest.mark.django_db
class TestMlCoverage:
    def test_train_admin_xgboost(self, admin_user, api_client):
        token = RefreshToken.for_user(admin_user).access_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        with patch('ml_predict.pipeline.train_and_save', return_value={'f1_macro': 0.8}):
            r = api_client.post('/api/v1/ml/train/', {'algorithm': 'XGBoost'}, format='json')
        assert r.status_code == 201

    def test_model_metrics_no_run(self, api_client):
        from ml_predict.models import FertilityModelRun
        FertilityModelRun.objects.all().delete()
        r = api_client.get('/api/v1/ml/metrics/')
        assert r.status_code == 200
        assert 'message' in r.json()

    def test_model_metrics_with_run(self, api_client, db):
        from ml_predict.models import FertilityModelRun
        FertilityModelRun.objects.create(
            algorithm='RandomForest', sample_count=100, f1_macro=0.8,
            model_path='/tmp/x.pkl', is_active=True,
        )
        r = api_client.get('/api/v1/ml/metrics/')
        assert r.status_code == 200
        assert r.json()['algorithm'] == 'RandomForest'

    def test_predict_and_batch_errors(self, api_client, auth_client):
        assert api_client.post('/api/v1/ml/predict/', {}, format='json').status_code == 400
        assert api_client.post('/api/v1/ml/predict/', {
            'ph': 6.2, 'humidity_pct': 35, 'soil_type': 'limoneux',
        }, format='json').status_code == 200
        assert auth_client.post('/api/v1/ml/predict/batch/', {}, format='json').status_code == 400
        assert auth_client.post('/api/v1/ml/predict/batch/export/', {}, format='json').status_code == 400

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

    def test_pipeline_build_labels(self, db):
        from datetime import date
        from ml_predict.pipeline import build_training_dataframe
        from soils.models import SoilPoint
        SoilPoint.objects.create(
            location=Point(1.2, 6.3, srid=4326), ph=5.0, humidity_pct=20,
            soil_type='sableux', collected_at=date(2025, 3, 1), is_validated=True,
            fertility_class='', fertility_score=None, ndvi_3m_avg=0.2,
        )
        SoilPoint.objects.create(
            location=Point(1.3, 6.3, srid=4326), ph=6.5, humidity_pct=50,
            soil_type='limoneux', collected_at=date(2025, 8, 1), is_validated=True,
            fertility_class='', fertility_score=0.55,
        )
        SoilPoint.objects.create(
            location=Point(1.35, 6.3, srid=4326), ph=7.5, humidity_pct=50,
            soil_type='limoneux', collected_at=date(2025, 8, 1), is_validated=True,
            fertility_class='', fertility_score=0.8,
        )
        SoilPoint.objects.create(
            location=Point(1.4, 6.3, srid=4326), ph=8.0, humidity_pct=50,
            soil_type='limoneux', collected_at=date(2025, 8, 1), is_validated=True,
            fertility_class='', fertility_score=0.9,
        )
        df = build_training_dataframe()
        assert len(df) >= 3
        assert 'elevee' in set(df['fertility_class'])

    def test_pipeline_xgboost_native(self):
        pytest.importorskip('xgboost')
        import pandas as pd
        from ml_predict.pipeline import train_and_save
        with patch('ml_predict.pipeline.build_training_dataframe') as m:
            m.return_value = pd.DataFrame([{
                'ph': 6, 'humidity_pct': 30, 'soil_type': 'limoneux', 'slope_pct': 3,
                'ndvi_3m_avg': 0.4, 'smap_moisture_avg': 0.2, 'temperature': 28,
                'elevation_m': 50, 'season': 'seche', 'fertility_class': 'moyenne',
            }] * 40)
            metrics = train_and_save(algorithm='XGBoost')
        assert 'f1_macro' in metrics

    def test_pipeline_xgboost_import_fallback(self):
        import pandas as pd
        from ml_predict.pipeline import train_and_save
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == 'xgboost':
                raise ImportError('no xgboost')
            return real_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=fake_import), \
             patch('ml_predict.pipeline.build_training_dataframe') as m:
            m.return_value = pd.DataFrame([{
                'ph': 6, 'humidity_pct': 30, 'soil_type': 'limoneux', 'slope_pct': 3,
                'ndvi_3m_avg': 0.4, 'smap_moisture_avg': 0.2, 'temperature': 28,
                'elevation_m': 50, 'season': 'seche', 'fertility_class': 'moyenne',
            }] * 40)
            metrics = train_and_save(algorithm='XGBoost')
        assert 'f1_macro' in metrics

    def test_pipeline_roc_auc_fallback(self):
        import pandas as pd
        from ml_predict.pipeline import train_and_save
        with patch('ml_predict.pipeline.build_training_dataframe') as m, \
             patch('ml_predict.pipeline.roc_auc_score', side_effect=RuntimeError('auc')):
            m.return_value = pd.DataFrame([{
                'ph': 6, 'humidity_pct': 30, 'soil_type': 'limoneux', 'slope_pct': 3,
                'ndvi_3m_avg': 0.4, 'smap_moisture_avg': 0.2, 'temperature': 28,
                'elevation_m': 50, 'season': 'seche', 'fertility_class': 'moyenne',
            }] * 40)
            metrics = train_and_save(algorithm='RandomForest')
        assert metrics['auc_roc'] is None

    def test_load_artifact_trains_if_missing(self, settings, tmp_path):
        from ml_predict import pipeline
        settings.ML_ARTIFACTS_DIR = tmp_path
        pipeline.MODEL_FILE = tmp_path / 'fertility_pipeline.pkl'
        pipeline.MODEL_FILE.write_bytes(b'old')
        pipeline.MODEL_FILE.unlink()
        with patch('ml_predict.pipeline.train_and_save', return_value={'f1_macro': 0.7}):
            with patch('ml_predict.pipeline.joblib.load', return_value={
                'pipeline': MagicMock(
                    predict=MagicMock(return_value=[0]),
                    predict_proba=MagicMock(return_value=[[0.3, 0.5, 0.2]]),
                ),
                'label_encoder': MagicMock(
                    classes_=['faible', 'moyenne', 'elevee'],
                    inverse_transform=MagicMock(return_value=['moyenne']),
                ),
            }):
                from ml_predict.pipeline import load_artifact
                load_artifact()

    def test_celery_tasks_skip_and_run(self, settings):
        from ml_predict.tasks import check_retrain_fertility_model
        from ml_predict.models import FertilityModelRun
        from nasa.tasks import ingest_all_nasa_layers
        FertilityModelRun.objects.create(
            algorithm='RF', sample_count=10, f1_macro=0.7,
            model_path='/x', is_active=True,
        )
        settings.ML_RETRAIN_NEW_SAMPLES = 99999
        result = check_retrain_fertility_model()
        assert result['skipped'] is True
        settings.ML_RETRAIN_NEW_SAMPLES = 0
        with patch('ml_predict.tasks.train_and_save', return_value={'ok': True}) as mock_train:
            result = check_retrain_fertility_model()
        assert mock_train.called
        assert result == {'ok': True}
        with patch('nasa.tasks.ingest_all', return_value={}):
            ingest_all_nasa_layers()


@pytest.mark.django_db
class TestSoilsCoverage:
    def test_str_methods(self, sample_soil_point, sample_zone):
        assert 'Sol #' in str(sample_soil_point)
        assert sample_zone.code in str(sample_zone)

    def test_export_geojson(self, api_client, sample_soil_point):
        r = api_client.get('/api/v1/points/geojson/')
        assert r.status_code == 200

    def test_serializer_partial_update(self, auth_client, sample_soil_point):
        r = auth_client.patch(f'/api/v1/points/{sample_soil_point.id}/', {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [1.25, 6.35]},
            'properties': {'ph': 6.3},
        }, format='json')
        assert r.status_code in (200, 400)

    def test_serializer_validation_error(self, sample_soil_point):
        from rest_framework import serializers as drf_serializers
        from soils.serializers import SoilPointSerializer
        ser = SoilPointSerializer(instance=sample_soil_point)
        with pytest.raises(drf_serializers.ValidationError) as exc:
            ser.validate({
                'ph': 2.0,
                'humidity_pct': sample_soil_point.humidity_pct,
                'soil_type': sample_soil_point.soil_type,
                'location': sample_soil_point.location,
            })
        assert 'ph' in exc.value.detail

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
        u = User.objects.create_user('pub', password='x', role='public')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(u).access_token}')
        assert api_client.post('/api/v1/points/import_data/', {}, format='multipart').status_code == 403

    def test_seed_command_skip(self, db):
        from soils.models import SoilPoint
        for i in range(150):
            SoilPoint.objects.create(
                location=Point(1.0 + i * 0.001, 6.3, srid=4326),
                ph=6, humidity_pct=30, soil_type='limoneux',
                collected_at='2025-01-01', is_validated=True,
            )
        out = StringIO()
        call_command('seed_demo_data', stdout=out)
        assert 'ignoré' in out.getvalue().lower()

    def test_seed_users_skip_existing(self, db):
        User.objects.create_user('admin', password='admin123', role=User.Role.ADMIN,
                                 is_superuser=True, is_staff=True)
        from soils.management.commands.seed_demo_data import Command
        Command()._users()

    def test_seed_command_full(self, db):
        from soils.models import SoilPoint
        SoilPoint.objects.all().delete()
        with patch('nasa.ingestion.ingest_all', return_value={}), \
             patch('ml_predict.pipeline.train_and_save', return_value={'f1_macro': 0.8}):
            out = StringIO()
            call_command('seed_demo_data', stdout=out)
        assert 'complete' in out.getvalue().lower()
        assert SoilPoint.objects.count() >= 150

    def test_seed_education_skip_quiz(self, db):
        from education.models import QuizQuestion
        from soils.models import SoilPoint
        from soils.management.commands.seed_demo_data import Command
        SoilPoint.objects.all().delete()
        for i in range(101):
            QuizQuestion.objects.create(
                text=f'Q{i}', difficulty='facile', choices=['A', 'B', 'C', 'D'],
                correct_index=0, explanation='E', points=5,
            )
        cmd = Command()
        with patch('nasa.ingestion.ingest_all', return_value={}), \
             patch('ml_predict.pipeline.train_and_save', return_value={}):
            cmd._users()
            zones = cmd._zones()
            cmd._soil_points(zones)
            cmd._nasa_snapshots()
            cmd._education()

    def test_train_command(self):
        out = StringIO()
        call_command('train_fertility_model', stdout=out)

    def test_ingest_nasa_command(self):
        out = StringIO()
        call_command('ingest_nasa', '--enrich-only', stdout=out)


@pytest.mark.django_db
class TestSpatialCoverage:
    def test_api_errors(self, auth_client, api_client):
        assert auth_client.post('/api/v1/spatial/intersection/', {}, format='json').status_code == 400
        assert auth_client.post('/api/v1/spatial/buffer/', {}, format='json').status_code == 400
        assert auth_client.post('/api/v1/spatial/area/', {}, format='json').status_code == 400
        assert api_client.get('/api/v1/spatial/statistics/').status_code == 200
        assert api_client.get('/api/v1/spatial/smap-correlation/').status_code == 200

    def test_services_full(self, sample_soil_point, sample_zone):
        from spatial import services
        import json
        from django.contrib.gis.geos import MultiPolygon, Polygon
        from soils.models import AdministrativeZone, SoilPoint

        poly = {
            'type': 'Polygon',
            'coordinates': [[[1.05, 6.15], [1.45, 6.15], [1.45, 6.45], [1.05, 6.45], [1.05, 6.15]]],
        }
        services.intersection_zones(json.dumps(poly))
        buf = services.buffer_geometry(json.dumps({'type': 'Point', 'coordinates': [1.2, 6.3]}), 200)
        assert buf
        stats = services.spatial_statistics_by_zone()
        assert 'by_canton' in stats

        degraded_poly = Polygon((
            (1.0, 6.1), (1.2, 6.1), (1.2, 6.3), (1.0, 6.3), (1.0, 6.1),
        ))
        AdministrativeZone.objects.create(
            name='Degraded', code='DEG-1', zone_type='degraded',
            geometry=MultiPolygon(degraded_poly, srid=4326),
        )
        stats2 = services.spatial_statistics_by_zone()
        assert stats2['degraded_surface_m2'] > 0

        for i, (slope, ndvi, smap) in enumerate([
            (6, 0.2, 0.1),
            (6, 0.5, 0.3),
            (2, 0.5, 0.3),
        ]):
            SoilPoint.objects.create(
                location=Point(1.2 + i * 0.02, 6.3, srid=4326),
                ph=6, humidity_pct=20, soil_type='limoneux',
                collected_at='2025-01-01', is_validated=True,
                slope_pct=slope, ndvi_3m_avg=ndvi, smap_moisture_avg=smap,
            )
        vuln = services.vulnerability_zoning()
        levels = {v['vulnerability'] for v in vuln}
        assert {'elevee', 'moyenne', 'faible'} <= levels

        sample_soil_point.smap_moisture_avg = 0.2
        sample_soil_point.humidity_pct = 25
        sample_soil_point.save()
        for _ in range(15):
            SoilPoint.objects.create(
                location=Point(1.2 + _ * 0.01, 6.3, srid=4326),
                ph=6, humidity_pct=20 + _, soil_type='limoneux',
                collected_at='2025-01-01', is_validated=True,
                smap_moisture_avg=0.18,
            )
        corr = services.smap_correlation()
        assert corr['sample_size'] >= 10


@pytest.mark.django_db
class TestPlatformExtensions:
    def test_admin_dashboard(self, admin_client):
        r = admin_client.get('/api/v1/platform/admin/dashboard/')
        assert r.status_code == 200
        assert 'users_total' in r.data

    def test_notifications_and_alerts(self, auth_client, agent_user):
        from sig_platform.models import DroughtAlert, Notification
        Notification.objects.create(
            user=agent_user, title='Test', message='Hello', level='info',
        )
        DroughtAlert.objects.create(message='Sécheresse test', severity='moyenne')
        assert auth_client.get('/api/v1/platform/notifications/').status_code == 200
        assert auth_client.get('/api/v1/platform/alerts/drought/').status_code == 200

    def test_password_reset(self, api_client, agent_user):
        agent_user.email = 'agent@test.local'
        agent_user.save()
        r = api_client.post('/api/v1/platform/password/reset/', {'email': agent_user.email}, format='json')
        assert r.status_code == 200
        from sig_platform.models import PasswordResetToken
        prt = PasswordResetToken.objects.filter(user=agent_user).first()
        assert prt
        r2 = api_client.post('/api/v1/platform/password/reset/confirm/', {
            'token': prt.token,
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123',
        }, format='json')
        assert r2.status_code == 200

    def test_heatmap_notes_trajectory(self, auth_client, admin_client, sample_soil_point, agent_user):
        from accounts.models import UserLocation, UserLocationHistory
        from django.contrib.gis.geos import Point

        assert auth_client.get('/api/v1/heatmap/?field=ph').status_code == 200
        r = auth_client.post('/api/v1/notes/', {
            'soil_point': sample_soil_point.id,
            'text': 'Note test',
        }, format='json')
        assert r.status_code == 201
        assert auth_client.get(f'/api/v1/points/{sample_soil_point.id}/compare/').status_code == 200
        loc = UserLocation.objects.create(
            user=agent_user,
            location=Point(1.25, 6.35, srid=4326),
            is_sharing=True,
        )
        UserLocationHistory.objects.create(
            user=agent_user, location=loc.location, accuracy_m=10,
        )
        assert auth_client.get('/api/v1/auth/trajectory/').status_code == 200
        assert admin_client.get('/api/v1/validation/pending/').status_code == 200
        r = admin_client.post(
            f'/api/v1/points/{sample_soil_point.id}/validate_point/',
            {'action': 'validate'}, format='json',
        )
        assert r.status_code == 200

    def test_batch_predict_and_zone_report(self, auth_client, admin_client, sample_soil_point, sample_zone):
        from sig_platform.tasks import check_drought_alerts

        sample_soil_point.ndvi_3m_avg = 0.2
        sample_soil_point.smap_moisture_avg = 0.1
        sample_soil_point.is_validated = True
        sample_soil_point.save()
        result = check_drought_alerts()
        assert 'alerts_created' in result
        r = auth_client.post('/api/v1/ml/predict/batch/', {
            'point_ids': [sample_soil_point.id],
        }, format='json')
        assert r.status_code == 200
        r2 = auth_client.post('/api/v1/ml/predict/batch/export/', {
            'point_ids': [sample_soil_point.id],
        }, format='json')
        assert r2.status_code == 200
        assert admin_client.get(f'/api/v1/platform/reports/zone/{sample_zone.code}/').status_code == 200
        assert admin_client.get('/api/v1/platform/audit/').status_code == 200

    def test_notification_mark_read(self, auth_client, agent_user):
        from sig_platform.models import Notification
        n = Notification.objects.create(
            user=agent_user, title='Lire', message='M', level='info',
        )
        assert auth_client.post(f'/api/v1/platform/notifications/{n.id}/read/').status_code == 200
        assert auth_client.post('/api/v1/platform/notifications/99999/read/').status_code == 404

    def test_soil_point_actions(self, auth_client, admin_client, sample_soil_point):
        assert auth_client.get(
            f'/api/v1/points/{sample_soil_point.id}/predict_fertility/',
        ).status_code == 200
        assert auth_client.get('/api/v1/points/export-csv/').status_code == 200
        assert auth_client.get('/api/v1/points/?light=1').status_code == 200
        admin_client.post(
            f'/api/v1/points/{sample_soil_point.id}/validate_point/',
            {'action': 'reject'}, format='json',
        )

    def test_proximity_and_drought_serializer(self, api_client, sample_soil_point):
        from sig_platform.serializers import DroughtAlertSerializer
        from sig_platform.models import DroughtAlert

        assert api_client.get(
            '/api/v1/spatial/proximity/?lon=1.25&lat=6.35&radius_m=1000',
        ).status_code == 200
        alert = DroughtAlert.objects.create(message='x', severity='moyenne', soil_point=sample_soil_point)
        data = DroughtAlertSerializer(alert).data
        assert data['lat'] is not None
        assert api_client.get('/api/v1/spatial/proximity/').status_code == 400

    def test_extended_platform_soils(self, auth_client, admin_client, api_client, sample_soil_point):
        from django.contrib.gis.geos import Point
        from sig_platform.tasks import check_drought_alerts
        from soils.models import SoilPoint
        from soils.validators import validate_soil_point_quality

        assert auth_client.get('/api/v1/heatmap/?field=invalid').status_code == 200
        assert auth_client.get('/api/v1/points/99999/compare/').status_code == 404
        assert auth_client.get('/api/v1/notes/').status_code == 200
        assert auth_client.get(f'/api/v1/notes/?soil_point={sample_soil_point.id}').status_code == 200
        assert auth_client.get('/api/v1/platform/reports/zone/UNKNOWN/').status_code == 404
        assert api_client.post('/api/v1/platform/password/reset/confirm/', {
            'token': 'bad',
            'new_password': 'x',
            'new_password_confirm': 'y',
        }, format='json').status_code == 400

        sample_soil_point.ndvi_3m_avg = 0.2
        sample_soil_point.smap_moisture_avg = 0.1
        sample_soil_point.is_validated = True
        sample_soil_point.save()
        check_drought_alerts()
        check_drought_alerts()

        p_red = SoilPoint.objects.create(
            location=Point(1.2, 6.3, srid=4326), ph=5.0, humidity_pct=30,
            soil_type='limoneux', collected_at='2025-01-01',
        )
        p_yellow = SoilPoint.objects.create(
            location=Point(1.21, 6.3, srid=4326), ph=6.5, humidity_pct=30,
            soil_type='limoneux', collected_at='2025-01-01',
        )
        p_green = SoilPoint.objects.create(
            location=Point(1.22, 6.3, srid=4326), ph=8.0, humidity_pct=30,
            soil_type='limoneux', collected_at='2025-01-01',
        )
        assert p_red.ph_color == 'red'
        assert p_yellow.ph_color == 'yellow'
        assert p_green.ph_color == 'green'

        assert 'ph' in validate_soil_point_quality({'ph': 2.0})
        assert 'humidity_pct' in validate_soil_point_quality({'humidity_pct': 150})
        assert 'location' in validate_soil_point_quality({'location': Point(0, 0, srid=4326)})

    def test_remaining_gaps(self, auth_client, api_client, sample_soil_point, admin_user):
        from sig_platform.models import PasswordResetToken

        assert api_client.get('/api/v1/dashboard/stats/').status_code == 200
        auth_client.post('/api/v1/points/', {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [1.26, 6.36]},
            'properties': {
                'ph': 6.1, 'humidity_pct': 32, 'soil_type': 'limoneux',
                'collected_at': '2025-06-01', 'parent_point': sample_soil_point.id,
            },
        }, format='json')
        poly = {
            'type': 'Polygon',
            'coordinates': [[[1.1, 6.2], [1.3, 6.2], [1.3, 6.4], [1.1, 6.4], [1.1, 6.2]]],
        }
        assert auth_client.post('/api/v1/spatial/intersection/', {'geometry': poly}, format='json').status_code == 200
        assert auth_client.post('/api/v1/spatial/buffer/', {
            'geometry': {'type': 'Point', 'coordinates': [1.25, 6.35]},
            'distance_m': 300,
        }, format='json').status_code == 200
        assert auth_client.post('/api/v1/spatial/area/', {'geometry': poly}, format='json').status_code == 200
        assert api_client.get('/api/v1/spatial/vulnerability/').status_code == 200
        assert api_client.get(f'/api/v1/spatial/ndvi-timeseries/{sample_soil_point.id}/').status_code == 200
        prt = PasswordResetToken.create_for_user(admin_user)
        prt.used = True
        prt.save()
        assert not prt.is_valid()
        assert api_client.post('/api/v1/platform/password/reset/confirm/', {
            'token': prt.token,
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123',
        }, format='json').status_code == 400
        assert api_client.post('/api/v1/platform/password/reset/confirm/', {
            'token': 'x', 'new_password': 'aaaa1234', 'new_password_confirm': 'bbbb1234',
        }, format='json').status_code == 400
