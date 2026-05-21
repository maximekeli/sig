"""Création de notifications in-app."""
from .models import Notification


def notify_user(user, title, message, *, link='', level=Notification.Level.INFO):
    if not user or not getattr(user, 'pk', None):
        return None
    return Notification.objects.create(
        user=user,
        title=title[:200],
        message=message,
        link=link[:300],
        level=level,
    )
