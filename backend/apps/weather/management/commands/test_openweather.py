"""Test connexion OpenWeather (météo Lomé)."""
from django.core.management.base import BaseCommand

from weather.client import OpenWeatherError, fetch_current, fetch_forecast, is_configured


class Command(BaseCommand):
    help = 'Vérifie OpenWeather sur la zone pilote (Lomé).'

    def handle(self, *args, **options):
        if not is_configured():
            self.stderr.write(self.style.ERROR('OPENWEATHER_API_KEY absent dans .env'))
            return

        lat, lon = 6.4, 1.35
        try:
            cur = fetch_current(lat, lon, force_refresh=True)
            c = cur['current']
            self.stdout.write(self.style.SUCCESS(
                f"Météo actuelle : {c['temp_c']}°C, {c['description']}, "
                f"humidité {c['humidity_pct']}%",
            ))
            fc = fetch_forecast(lat, lon, force_refresh=True)
            self.stdout.write(self.style.SUCCESS(
                f"Prévisions : {len(fc['forecast'])} créneaux ({fc.get('city', '')})",
            ))
        except OpenWeatherError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
