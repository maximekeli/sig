from django.contrib.auth.models import AbstractUser
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
