"""Test connexion Sentinel Hub (OAuth + Process API léger)."""
from django.core.management.base import BaseCommand

from sentinel.client import (
    SentinelHubError,
    get_access_token,
    has_secret,
    is_configured,
    process_image,
)


class Command(BaseCommand):
    help = 'Vérifie OAuth Sentinel Hub et une requête Process API (bbox Maritime).'

    def handle(self, *args, **options):
        if not has_secret():
            self.stderr.write(self.style.ERROR(
                'SENTINEL_HUB_CLIENT_SECRET / SENTINEL_HUB_API_KEY absent dans .env',
            ))
            return

        if not is_configured():
            self.stderr.write(self.style.WARNING(
                'Secret présent mais SENTINEL_HUB_CLIENT_ID manquant. '
                'Ajoutez le Client ID (UUID) depuis apps.sentinel-hub.com → OAuth clients.',
            ))
            return

        try:
            token = get_access_token(force_refresh=True)
            self.stdout.write(self.style.SUCCESS(
                f'OAuth OK — jeton obtenu ({len(token)} caractères)',
            ))
        except SentinelHubError as exc:
            self.stderr.write(self.style.ERROR(f'OAuth échoué : {exc}'))
            return

        bbox = (1.1, 6.2, 1.3, 6.4)
        try:
            png = process_image('ndvi', bbox, width=128, height=128, days_back=45)
            self.stdout.write(self.style.SUCCESS(
                f'Process API OK — image NDVI {len(png)} octets (bbox {bbox})',
            ))
        except SentinelHubError as exc:
            self.stderr.write(self.style.ERROR(f'Process API échoué : {exc}'))
