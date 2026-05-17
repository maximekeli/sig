from rest_framework.permissions import BasePermission

from .models import User


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_administrator
        )


class IsAgentOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_agent
        )
