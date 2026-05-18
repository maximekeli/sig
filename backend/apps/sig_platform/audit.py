"""Journal d'audit centralisé."""
from .models import AuditLog


def log_action(user, action, resource, resource_id='', detail=None):
    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        resource=resource,
        resource_id=str(resource_id) if resource_id else '',
        detail=detail or {},
    )
