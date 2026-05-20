import pytest
from django.test import override_settings


@pytest.mark.django_db
def test_assistant_status_no_key(api_client):
    with override_settings(GEMINI_API_KEY=''):
        r = api_client.get('/api/v1/assistant/status/')
    assert r.status_code == 200
    assert r.json()['available'] is False


@pytest.mark.django_db
def test_assistant_status_with_key(api_client):
    with override_settings(GEMINI_API_KEY='test-key', GEMINI_MODEL='gemini-2.0-flash'):
        r = api_client.get('/api/v1/assistant/status/')
    assert r.status_code == 200
    assert r.json()['available'] is True
    assert r.json()['model'] == 'gemini-2.0-flash'


@pytest.mark.django_db
def test_assistant_chat_requires_message(api_client):
    r = api_client.post('/api/v1/assistant/chat/', {'message': '  '}, format='json')
    assert r.status_code == 400


@pytest.mark.django_db
def test_assistant_chat_no_key(api_client):
    with override_settings(GEMINI_API_KEY=''):
        r = api_client.post('/api/v1/assistant/chat/', {
            'message': 'Bonjour',
        }, format='json')
    assert r.status_code == 503
    assert 'error' in r.json()


@pytest.mark.django_db
def test_assistant_chat_mocked(api_client, monkeypatch):
    with override_settings(GEMINI_API_KEY='fake-key'):
        monkeypatch.setattr(
            'assistant.views.chat_with_gemini',
            lambda message, history=None, context=None: ('Bonjour ! Je suis l\'assistant SIG Sols.', None),
        )
        r = api_client.post('/api/v1/assistant/chat/', {
            'message': 'Bonjour',
            'context': {'view': 'map'},
        }, format='json')
    assert r.status_code == 200
    assert 'assistant' in r.json()['reply'].lower() or 'SIG' in r.json()['reply']
