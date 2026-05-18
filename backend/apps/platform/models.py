import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'create', 'Création'
        UPDATE = 'update', 'Modification'
        DELETE = 'delete', 'Suppression'
        IMPORT = 'import', 'Import'
        VALIDATE = 'validate', 'Validation'
        LOGIN = 'login', 'Connexion'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    resource = models.CharField(max_length=80)
    resource_id = models.CharField(max_length=64, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['resource', 'created_at'])]


class Notification(models.Model):
    class Level(models.TextChoices):
        INFO = 'info', 'Info'
        WARNING = 'warning', 'Avertissement'
        ALERT = 'alert', 'Alerte'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications',
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.INFO)
    link = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class DroughtAlert(models.Model):
    """Alerte sécheresse / stress hydrique sur une zone ou un point."""

    zone = models.ForeignKey(
        'soils.AdministrativeZone', null=True, blank=True, on_delete=models.CASCADE,
    )
    soil_point = models.ForeignKey(
        'soils.SoilPoint', null=True, blank=True, on_delete=models.CASCADE,
    )
    ndvi = models.FloatField(null=True, blank=True)
    smap = models.FloatField(null=True, blank=True)
    severity = models.CharField(max_length=20, default='moyenne')
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def create_for_user(cls, user):
        token = secrets.token_urlsafe(32)
        return cls.objects.create(user=user, token=token)

    def is_valid(self):
        if self.used:
            return False
        expiry = self.created_at + timedelta(hours=24)
        return timezone.now() < expiry
