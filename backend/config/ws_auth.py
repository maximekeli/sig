"""Authentification WebSocket : JWT (mobile) ou session Django (web)."""
from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token: str):
    try:
        validated = AccessToken(token)
        return User.objects.get(pk=validated['user_id'])
    except (InvalidToken, TokenError, User.DoesNotExist, KeyError):
        return AnonymousUser()


class TokenOrSessionAuthMiddleware:
    """JWT via ?token= pour mobile ; session cookie pour le site web."""

    def __init__(self, inner):
        self.inner = inner
        self.session_stack = AuthMiddlewareStack(inner)

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'websocket':
            return await self.inner(scope, receive, send)

        query = parse_qs(scope.get('query_string', b'').decode())
        token = (query.get('token') or [None])[0]
        if token:
            scope['user'] = await get_user_from_token(token)
            return await self.inner(scope, receive, send)

        return await self.session_stack(scope, receive, send)
