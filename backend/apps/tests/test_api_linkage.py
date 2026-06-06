"""
Tests de liaison API — vérifie que tous les endpoints utilisés par le site web
et l'application mobile répondent correctement (même contrat backend ↔ clients).
"""
import pytest
from django.test import override_settings
from rest_framework_simplejwt.tokens import RefreshToken


PARCEL_GEOMETRY = {
    'type': 'Polygon',
    'coordinates': [
        [
            [1.34, 6.39],
            [1.36, 6.39],
            [1.36, 6.41],
            [1.34, 6.41],
            [1.34, 6.39],
        ],
    ],
}

POINT_FEATURE = {
    'type': 'Feature',
    'geometry': {'type': 'Point', 'coordinates': [1.26, 6.36]},
    'properties': {
        'ph': 6.2,
        'humidity_pct': 35,
        'soil_type': 'limoneux',
        'collected_at': '2026-01-15',
        'source': 'terrain',
    },
}


def _token_client(api_client, user):
    token = RefreshToken.for_user(user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.mark.django_db
class TestLinkagePublicEndpoints:
    """Endpoints accessibles sans authentification (site web + mobile)."""

    def test_health_detail(self, api_client):
        r = api_client.get('/health/?detail=1')
        assert r.status_code == 200
        body = r.json()
        assert body['status'] in ('ok', 'degraded')
        assert body['checks']['database'] == 'ok'
        assert body['checks']['database_info']['backend'] in ('postgis', 'sqlite')
        assert 'web,mobile' in body['checks']['database_info']['clients']

    def test_points_light(self, api_client, sample_soil_point):
        r = api_client.get('/api/v1/points/?light=1&is_validated=true')
        assert r.status_code == 200

    def test_dashboard_and_ml_metrics(self, api_client, sample_soil_point):
        assert api_client.get('/api/v1/dashboard/stats/').status_code == 200
        assert api_client.get('/api/v1/ml/metrics/').status_code == 200

    def test_nasa_endpoints(self, api_client):
        assert api_client.get('/api/v1/nasa/catalog/summary/').status_code == 200
        assert api_client.get('/api/v1/nasa/layers/').status_code == 200

    def test_sentinel_status_and_layers(self, api_client):
        assert api_client.get('/api/v1/sentinel/status/').status_code == 200
        assert api_client.get('/api/v1/sentinel/layers/').status_code == 200

    def test_weather_status(self, api_client):
        r = api_client.get('/api/v1/weather/status/')
        assert r.status_code == 200
        assert 'configured' in r.json()

    def test_assistant_status(self, api_client):
        assert api_client.get('/api/v1/assistant/status/').status_code == 200

    def test_spatial_public(self, api_client, sample_soil_point):
        r = api_client.get('/api/v1/spatial/proximity/?lon=1.25&lat=6.35&radius_m=5000')
        assert r.status_code == 200
        assert r.json()['count'] >= 1
        assert api_client.get('/api/v1/spatial/smap-correlation/').status_code == 200
        assert api_client.get('/api/v1/spatial/parcel/zones/').status_code == 200
        geo = api_client.get('/api/v1/spatial/parcel/zones/geojson/?types=canton,degraded')
        assert geo.status_code == 200

    def test_parcel_live_minimal(self, api_client):
        r = api_client.post('/api/v1/spatial/parcel/live/', {
            'geometry': PARCEL_GEOMETRY,
            'use_sentinel': False,
            'use_weather': False,
            'use_ml': False,
        }, format='json')
        assert r.status_code == 200
        body = r.json()
        assert 'parcel_name' in body or 'area' in body

    def test_ml_predict(self, api_client):
        r = api_client.post('/api/v1/ml/predict/', {
            'ph': 6.0,
            'humidity_pct': 40,
            'soil_type': 'limoneux',
            'lat': 6.35,
            'lon': 1.25,
        }, format='json')
        assert r.status_code == 200
        assert r.json()['predicted_class'] in ('faible', 'moyenne', 'elevee')

    def test_heatmap(self, api_client, sample_soil_point):
        assert api_client.get('/api/v1/heatmap/?field=ph').status_code == 200

    def test_education_public(self, api_client):
        assert api_client.get('/api/v1/education/quiz/stats/').status_code == 200
        assert api_client.get('/api/v1/education/quiz/leaderboard/').status_code == 200
        assert api_client.get('/api/v1/education/sheets/').status_code == 200

    def test_videos_public(self, api_client):
        assert api_client.get('/api/v1/videos/posts/?kind=video').status_code == 200
        assert api_client.get('/api/v1/videos/stories/').status_code == 200


@pytest.mark.django_db
class TestLinkageAuthenticated:
    """Endpoints nécessitant JWT (web + mobile après login)."""

    def test_auth_token_and_profile(self, api_client, agent_user):
        r = api_client.post('/api/v1/auth/token/', {
            'username': 'test_agent',
            'password': 'testpass123',
        }, format='json')
        assert r.status_code == 200
        assert r.json()['access']
        assert r.json()['user']['username'] == 'test_agent'

        client = _token_client(api_client, agent_user)
        prof = client.get('/api/v1/auth/profile/')
        assert prof.status_code == 200

    def test_create_soil_point_geojson(self, auth_client):
        """Même format que frontend/js/features.js et mobile OfflineQueueService."""
        r = auth_client.post('/api/v1/points/', POINT_FEATURE, format='json')
        assert r.status_code in (200, 201)

    def test_ndvi_timeseries(self, api_client, sample_soil_point):
        r = api_client.get(f'/api/v1/spatial/ndvi-timeseries/{sample_soil_point.pk}/')
        assert r.status_code == 200

    def test_location_update(self, auth_client):
        r = auth_client.post('/api/v1/auth/location/', {
            'lat': 6.4,
            'lon': 1.35,
        }, format='json')
        assert r.status_code == 200

    def test_feed_and_quiz_badges(self, auth_client):
        assert auth_client.get('/api/v1/auth/feed/').status_code == 200
        assert auth_client.get('/api/v1/education/quiz/badges/').status_code == 200

    def test_notifications(self, auth_client):
        assert auth_client.get('/api/v1/platform/notifications/').status_code == 200
        unread = auth_client.get('/api/v1/platform/notifications/unread-count/')
        assert unread.status_code == 200
        assert 'count' in unread.json()

    def test_quiz_full_flow(self, auth_client):
        from education.models import QuizQuestion
        QuizQuestion.objects.create(
            text='Liaison?', difficulty='facile',
            choices=['A', 'B', 'C', 'D'], correct_index=0,
            explanation='OK', points=5,
        )
        start = auth_client.post('/api/v1/education/quiz/start/', {
            'difficulty': 'facile', 'count': 1,
        }, format='json')
        assert start.status_code == 200
        sid = start.json()['session_id']
        qid = start.json()['questions'][0]['id']
        ans = auth_client.post(f'/api/v1/education/quiz/{sid}/answer/', {
            'question_id': qid, 'selected_index': 0,
        }, format='json')
        assert ans.status_code == 200
        fin = auth_client.post(f'/api/v1/education/quiz/{sid}/finish/', {}, format='json')
        assert fin.status_code == 200

    def test_assistant_chat_mocked(self, api_client, monkeypatch):
        with override_settings(GEMINI_API_KEY='fake-key'):
            monkeypatch.setattr(
                'assistant.views.chat_with_gemini',
                lambda message, history=None, context=None: ('Réponse test liaison.', None),
            )
            r = api_client.post('/api/v1/assistant/chat/', {
                'message': 'Test liaison',
                'context': {},
            }, format='json')
        assert r.status_code == 200
        assert r.json()['reply']

    def test_sentinel_analyze_mocked(self, api_client, monkeypatch):
        monkeypatch.setattr(
            'sentinel.views.analyze_ndvi_bbox',
            lambda bbox: {'ndvi_mean': 0.42, 'ok': True},
        )
        r = api_client.post('/api/v1/sentinel/analyze/', {
            'bbox': [1.0, 6.0, 1.5, 6.5],
        }, format='json')
        assert r.status_code == 200

    def test_weather_current_mocked(self, api_client, monkeypatch):
        with override_settings(OPENWEATHER_API_KEY='test-key'):
            monkeypatch.setattr(
                'weather.views.fetch_current',
                lambda lat, lon: {
                    'temp_c': 28,
                    'humidity_pct': 70,
                    'description': 'nuageux',
                },
            )
            r = api_client.get('/api/v1/weather/current/?lat=6.4&lon=1.35')
        assert r.status_code == 200

    def test_activity_ping(self, auth_client):
        r = auth_client.post('/api/v1/platform/activity/', {
            'action': 'test_linkage',
            'meta': {},
            'source': 'test',
        }, format='json')
        assert r.status_code == 200


@pytest.mark.django_db
class TestLinkageAgentAdmin:
    """Endpoints agent / admin (site web avancé)."""

    def test_validation_pending(self, auth_client, sample_soil_point):
        sample_soil_point.is_validated = False
        sample_soil_point.save(update_fields=['is_validated'])
        r = auth_client.get('/api/v1/validation/pending/')
        assert r.status_code == 200

    def test_drought_alerts(self, auth_client):
        assert auth_client.get('/api/v1/platform/alerts/drought/').status_code == 200

    def test_admin_dashboard(self, admin_client):
        assert admin_client.get('/api/v1/platform/admin/dashboard/').status_code == 200

    def test_user_search(self, auth_client):
        r = auth_client.get('/api/v1/auth/users/search/?q=test')
        assert r.status_code == 200
