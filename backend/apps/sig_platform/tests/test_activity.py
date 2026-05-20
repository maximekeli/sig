import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def _reg_payload(**overrides):
    data = {
        'username': 'trackuser',
        'email': 'track@test.tg',
        'password': 'securepass123',
        'password_confirm': 'securepass123',
        'first_name': 'Track',
        'last_name': 'User',
        'age': 28,
        'consent_analytics': True,
        'role': 'public',
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_activity_ingest_anonymous(api_client):
    r = api_client.post('/api/v1/platform/activity/', {
        'session_id': 'sess-anon-1',
        'events': [{
            'event_type': 'map_zoom',
            'category': 'map',
            'view_name': 'map',
            'detail': {'zoom': 10},
        }],
    }, format='json')
    assert r.status_code == 200
    assert r.json()['accepted'] == 1


@pytest.mark.django_db
def test_activity_ingest_authenticated_with_consent(api_client):
    api_client.post('/api/v1/auth/register/', _reg_payload(), format='json')
    token = RefreshToken.for_user(User.objects.get(username='trackuser')).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    r = api_client.post('/api/v1/platform/activity/', {
        'session_id': 'sess-auth-1',
        'events': [
            {'event_type': 'map_zoom', 'category': 'map', 'view_name': 'map', 'detail': {'zoom': 11}},
            {'event_type': 'view_open', 'category': 'navigation', 'view_name': 'quiz', 'detail': {}},
        ],
    }, format='json')
    assert r.status_code == 200
    assert r.json()['accepted'] == 2


@pytest.mark.django_db
def test_activity_rejected_without_consent(api_client):
    User.objects.create_user(
        username='noconsent',
        password='securepass123',
        consent_analytics=False,
    )
    token = RefreshToken.for_user(User.objects.get(username='noconsent')).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    r = api_client.post('/api/v1/platform/activity/', {
        'session_id': 'sess-no',
        'events': [{'event_type': 'map_zoom', 'category': 'map', 'view_name': 'map', 'detail': {}}],
    }, format='json')
    assert r.status_code == 200
    assert r.json()['accepted'] == 0


@pytest.mark.django_db
def test_analytics_summary_admin(admin_client):
    r = admin_client.get('/api/v1/platform/admin/analytics/?days=7')
    assert r.status_code == 200
    body = r.json()
    assert 'events_total' in body
    assert 'map_zoom_total' in body
    assert 'age_distribution' in body


@pytest.mark.django_db
def test_user_activity_detail_admin(admin_client, agent_user):
    from sig_platform.models import UserActivityEvent
    UserActivityEvent.objects.create(
        user=agent_user,
        session_id='adm-test',
        event_type='quiz_start',
        category='quiz',
        view_name='quiz',
        detail={'count': 5},
    )
    r = admin_client.get(f'/api/v1/platform/admin/activity/users/{agent_user.id}/')
    assert r.status_code == 200
    body = r.json()
    assert body['events_total'] >= 1
    assert body['user']['username'] == 'test_agent'
