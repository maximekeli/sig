import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_register_and_token(api_client):
    r = api_client.post('/api/v1/auth/register/', {
        'username': 'newuser',
        'email': 'n@test.tg',
        'password': 'securepass123',
        'role': 'public',
    })
    assert r.status_code == 201
    r2 = api_client.post('/api/v1/auth/token/', {
        'username': 'newuser',
        'password': 'securepass123',
    })
    assert r2.status_code == 200
    assert 'access' in r2.json()


@pytest.mark.django_db
def test_register_cannot_self_assign_admin(api_client):
    r = api_client.post('/api/v1/auth/register/', {
        'username': 'hacker',
        'password': 'securepass123',
        'role': 'admin',
    })
    assert r.status_code == 201
    user = User.objects.get(username='hacker')
    assert user.role == User.Role.PUBLIC


@pytest.mark.django_db
def test_profile_authenticated(auth_client, agent_user):
    r = auth_client.get('/api/v1/auth/profile/')
    assert r.status_code == 200
    assert r.json()['username'] == 'test_agent'


@pytest.mark.django_db
def test_user_list_requires_admin(api_client, agent_user, admin_user):
    from rest_framework_simplejwt.tokens import RefreshToken
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(agent_user).access_token}')
    assert api_client.get('/api/v1/auth/users/').status_code == 403
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(admin_user).access_token}')
    assert api_client.get('/api/v1/auth/users/').status_code == 200


@pytest.mark.django_db
def test_health():
    from django.test import Client
    c = Client()
    r = c.get('/health/')
    assert r.status_code == 200
    assert 'SIG-SOLS' in r.json()['project']
