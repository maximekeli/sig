import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_register_and_token(api_client):
    User.objects.create_user(username='existing', password='testpass123')
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
def test_health():
    from django.test import Client
    c = Client()
    r = c.get('/health/')
    assert r.status_code == 200
    assert 'SIG-SOLS' in r.json()['project']
