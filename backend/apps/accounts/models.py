from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.db import models


class User(AbstractUser):
    """Three roles per ToR: Administrateur, Agent, Public."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrateur'
        AGENT = 'agent', 'Agent'
        PUBLIC = 'public', 'Public'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PUBLIC,
    )
    organization = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    pseudonym = models.CharField(
        max_length=50,
        blank=True,
        help_text='For quiz leaderboard anonymization',
    )

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    @property
    def is_administrator(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_agent(self):
        return self.role in (self.Role.AGENT, self.Role.ADMIN) or self.is_staff

    @property
    def display_name(self):
        return self.pseudonym or self.get_full_name() or self.username


class UserLocation(models.Model):
    """Position GPS en temps réel d'un utilisateur connecté."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='live_location',
    )
    location = gis_models.PointField(srid=4326)
    accuracy_m = models.FloatField(null=True, blank=True)
    heading = models.FloatField(null=True, blank=True)
    is_sharing = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Position utilisateur'
        verbose_name_plural = 'Positions utilisateurs'
        indexes = [
            models.Index(fields=['is_sharing', 'updated_at']),
        ]

    def __str__(self):
        return f'{self.user.username} @ {self.updated_at:%H:%M:%S}'


class UserLocationHistory(models.Model):
    """Trajectoire GPS (historique des positions)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='location_history',
    )
    location = gis_models.PointField(srid=4326)
    accuracy_m = models.FloatField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [models.Index(fields=['user', 'recorded_at'])]
