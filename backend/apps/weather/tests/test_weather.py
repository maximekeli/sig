from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

SAMPLE_CURRENT = {
    'name': 'Lomé',
    'main': {'temp': 28.5, 'feels_like': 30, 'humidity': 72, 'pressure': 1012},
    'weather': [{'description': 'nuages dispersés', 'icon': '03d'}],
    'wind': {'speed': 3.2, 'deg': 180},
    'clouds': {'all': 40},
    'dt': 1710000000,
    'sys': {'sunrise': 1, 'sunset': 2},
}

SAMPLE_FORECAST = {
    'city': {'name': 'Lomé'},
    'list': [
        {
            'dt': 1710000000,
            'main': {'temp': 27, 'humidity': 70},
            'weather': [{'description': 'pluie légère', 'icon': '10d'}],
            'pop': 0.4,
        },
    ],
}


@override_settings(
    OPENWEATHER_API_KEY='test-ow-key',
    REGION_MARITIME_BBOX=(0.9, 6.0, 1.8, 6.8),
    OPENWEATHER_CACHE_SECONDS=600,
)
class OpenWeatherClientTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_is_configured(self):
        from weather.client import is_configured
        self.assertTrue(is_configured())

    @patch('weather.client.requests.get')
    def test_fetch_current(self, mock_get):
        from weather.client import fetch_current

        mock_get.return_value = MagicMock(
            ok=True,
            status_code=200,
            json=lambda: SAMPLE_CURRENT,
        )
        data = fetch_current(6.4, 1.35, force_refresh=True)
        self.assertEqual(data['current']['temp_c'], 28.5)
        self.assertEqual(data['current']['description'], 'nuages dispersés')

    @patch('weather.client.requests.get')
    def test_weather_summary(self, mock_get):
        from weather.client import weather_summary_for_point

        mock_get.return_value = MagicMock(
            ok=True,
            status_code=200,
            json=lambda: SAMPLE_CURRENT,
        )
        summary = weather_summary_for_point(6.4, 1.35)
        self.assertTrue(summary['configured'])
        self.assertIn('current', summary)

    def test_fetch_current_outside_region(self):
        from weather.client import OpenWeatherError, fetch_current

        with self.assertRaises(OpenWeatherError) as ctx:
            fetch_current(10.0, 10.0)
        self.assertIn('hors zone', str(ctx.exception))

    @override_settings(OPENWEATHER_API_KEY='')
    def test_fetch_without_api_key(self):
        from weather.client import OpenWeatherError, fetch_current

        with self.assertRaises(OpenWeatherError) as ctx:
            fetch_current(6.4, 1.35)
        self.assertIn('non configuré', str(ctx.exception))

    @patch('weather.client.requests.get')
    def test_fetch_current_uses_cache(self, mock_get):
        from weather.client import fetch_current

        mock_get.return_value = MagicMock(
            ok=True,
            status_code=200,
            json=lambda: SAMPLE_CURRENT,
        )
        fetch_current(6.4, 1.35, force_refresh=True)
        fetch_current(6.4, 1.35)
        self.assertEqual(mock_get.call_count, 1)

    @patch('weather.client.requests.get')
    def test_fetch_forecast(self, mock_get):
        from weather.client import fetch_forecast

        mock_get.return_value = MagicMock(
            ok=True,
            status_code=200,
            json=lambda: SAMPLE_FORECAST,
        )
        data = fetch_forecast(6.4, 1.35, force_refresh=True)
        self.assertEqual(data['city'], 'Lomé')
        self.assertEqual(len(data['forecast']), 1)
        self.assertEqual(data['forecast'][0]['description'], 'pluie légère')
        self.assertEqual(data['forecast'][0]['pop'], 0.4)

    @patch('weather.client.requests.get')
    def test_weather_summary_agro_tips_heat(self, mock_get):
        from weather.client import weather_summary_for_point

        hot = {**SAMPLE_CURRENT, 'main': {**SAMPLE_CURRENT['main'], 'temp': 36.0}}
        mock_get.return_value = MagicMock(ok=True, status_code=200, json=lambda: hot)
        summary = weather_summary_for_point(6.4, 1.35)
        self.assertTrue(any('chaleur' in t.lower() for t in summary.get('agro_tips', [])))

    @patch('weather.client.requests.get')
    def test_http_error_raises(self, mock_get):
        from weather.client import OpenWeatherError, fetch_current

        mock_get.return_value = MagicMock(ok=False, status_code=401, text='Invalid API key')
        with self.assertRaises(OpenWeatherError) as ctx:
            fetch_current(6.4, 1.35, force_refresh=True)
        self.assertIn('401', str(ctx.exception))


@override_settings(
    OPENWEATHER_API_KEY='test-ow-key',
    REGION_MARITIME_BBOX=(0.9, 6.0, 1.8, 6.8),
)
class OpenWeatherAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()

    def test_status_ok(self):
        r = self.client.get('/api/v1/weather/status/')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data['ok'])

    @override_settings(OPENWEATHER_API_KEY='')
    def test_status_not_configured(self):
        r = self.client.get('/api/v1/weather/status/')
        self.assertFalse(r.data['configured'])

    @patch('weather.views.fetch_current')
    def test_current_endpoint(self, mock_fetch):
        mock_fetch.return_value = {
            'lat': 6.4,
            'lon': 1.35,
            'current': {'temp_c': 28, 'description': 'ensoleillé'},
            'provider': 'OpenWeatherMap',
        }
        r = self.client.get('/api/v1/weather/current/?lat=6.4&lon=1.35')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['current']['temp_c'], 28)

    @patch('weather.views.fetch_forecast')
    def test_forecast_endpoint(self, mock_fetch):
        mock_fetch.return_value = {'forecast': [{'temp_c': 26}], 'city': 'Lomé'}
        r = self.client.get('/api/v1/weather/forecast/?lat=6.4&lon=1.35')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['forecast']), 1)

    def test_current_outside_region(self):
        r = self.client.get('/api/v1/weather/current/?lat=10&lon=10')
        self.assertEqual(r.status_code, 502)

    def test_current_missing_params(self):
        r = self.client.get('/api/v1/weather/current/')
        self.assertEqual(r.status_code, 400)
        self.assertIn('lat', r.data['detail'].lower())

    def test_forecast_missing_params(self):
        r = self.client.get('/api/v1/weather/forecast/')
        self.assertEqual(r.status_code, 400)
