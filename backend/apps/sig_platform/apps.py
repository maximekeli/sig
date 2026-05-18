from django.apps import AppConfig


class PlatformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sig_platform'
    verbose_name = 'Plateforme SIG Sols'

    def ready(self):
        import sig_platform.signals  # noqa: F401
