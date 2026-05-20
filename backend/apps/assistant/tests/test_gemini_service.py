"""Tests unitaires du service Gemini."""
from django.test import override_settings

from assistant.services.gemini import chat_with_gemini, is_available


def test_is_available_false():
    with override_settings(GEMINI_API_KEY=''):
        assert is_available() is False


def test_is_available_true():
    with override_settings(GEMINI_API_KEY='abc'):
        assert is_available() is True


def test_chat_without_api_key():
    with override_settings(GEMINI_API_KEY=''):
        reply, err = chat_with_gemini('Bonjour')
    assert reply is None
    assert 'GEMINI_API_KEY' in err


def test_chat_strips_empty_history():
    with override_settings(GEMINI_API_KEY=''):
        reply, err = chat_with_gemini(
            'Hi',
            history=[{'role': 'user', 'content': ''}, {'role': 'assistant', 'content': '   '}],
        )
    assert reply is None
    assert err
