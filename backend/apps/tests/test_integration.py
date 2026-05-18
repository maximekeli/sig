"""Tests d'intégration API — parcours complets."""
import pytest
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
class TestIntegrationFlow:
    def test_public_read_agent_write(self, api_client, agent_user, sample_soil_point):
        r = api_client.get('/api/v1/points/?light=1')
        assert r.status_code == 200

        token = RefreshToken.for_user(agent_user).access_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        r2 = api_client.get('/api/v1/auth/profile/')
        assert r2.status_code == 200

    def test_ml_predict_flow(self, api_client):
        r = api_client.post('/api/v1/ml/predict/', {
            'ph': 6.0,
            'humidity_pct': 40,
            'soil_type': 'limoneux',
            'ndvi_3m_avg': 0.5,
        }, format='json')
        assert r.status_code == 200
        body = r.json()
        assert body['predicted_class'] in ('faible', 'moyenne', 'elevee')
        assert body['inference_ms'] < 3000

    def test_spatial_proximity_with_data(self, api_client, sample_soil_point):
        r = api_client.get(
            '/api/v1/spatial/proximity/?lon=1.25&lat=6.35&radius_m=10000',
        )
        assert r.status_code == 200
        assert r.json()['count'] >= 1

    def test_nasa_and_dashboard(self, api_client, sample_soil_point):
        from nasa.ingestion import ingest_product
        ingest_product('MOD13Q1', 'test', days_back=2)
        assert api_client.get('/api/v1/nasa/layers/').status_code == 200
        stats = api_client.get('/api/v1/dashboard/stats/').json()
        assert stats['total_points'] >= 1

    def test_education_quiz_flow(self, auth_client, db):
        from education.models import QuizQuestion
        QuizQuestion.objects.create(
            text='Test?', difficulty='facile',
            choices=['A', 'B', 'C', 'D'], correct_index=0,
            explanation='Explication', points=5,
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
