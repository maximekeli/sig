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


@pytest.mark.django_db
def test_assistant_chat_with_history(api_client, monkeypatch):
    with override_settings(GEMINI_API_KEY='fake-key'):
        monkeypatch.setattr(
            'assistant.views.chat_with_gemini',
            lambda message, history=None, context=None: (
                f'ok:{len(history or [])}:{message[:10]}',
                None,
            ),
        )
        r = api_client.post('/api/v1/assistant/chat/', {
            'message': 'Suite',
            'history': [
                {'role': 'user', 'content': 'Première question'},
                {'role': 'assistant', 'content': 'Première réponse'},
            ],
            'context': {'view': 'quiz'},
        }, format='json')
    assert r.status_code == 200
    assert r.json()['reply'] == 'ok:2:Suite'


@pytest.mark.django_db
def test_assistant_chat_message_too_long(api_client):
    r = api_client.post('/api/v1/assistant/chat/', {
        'message': 'x' * 5000,
    }, format='json')
    assert r.status_code == 400


@pytest.mark.gemini_live
@pytest.mark.django_db
def test_assistant_chat_live_gemini(api_client):
    """Appel réel Gemini — exécuter avec GEMINI_LIVE_TESTS=1 et GEMINI_API_KEY valide."""
    import os
    if os.environ.get('GEMINI_LIVE_TESTS') != '1':
        pytest.skip('GEMINI_LIVE_TESTS=1 requis')
    from django.conf import settings
    if not settings.GEMINI_API_KEY:
        pytest.skip('GEMINI_API_KEY manquante')
    r = api_client.post('/api/v1/assistant/chat/', {
        'message': 'En une phrase : qu’est-ce que le pH du sol ?',
        'context': {'view': 'help'},
    }, format='json')
    if r.status_code == 503 and '429' in r.content.decode():
        pytest.skip('Quota API Gemini dépassé — réessayez plus tard ou activez la facturation.')
    assert r.status_code == 200, r.content
    reply = r.json().get('reply', '')
    assert len(reply) > 20
    assert 'pH' in reply or 'sol' in reply.lower()
