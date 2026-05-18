from django.apps import AppConfig


class PlatformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'platform'
    verbose_name = 'Plateforme SIG Sols'

    def ready(self):
        import platform.signals  # noqa: F401
