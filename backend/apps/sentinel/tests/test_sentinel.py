from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient


@override_settings(
    SENTINEL_HUB_CLIENT_ID='test-client-id',
    SENTINEL_HUB_CLIENT_SECRET='test-secret',
    REGION_MARITIME_BBOX=(0.9, 6.0, 1.8, 6.8),
)
class SentinelHubAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('sentinel.client.cache.get', return_value=None)
    @patch('sentinel.client.cache.set')
    @patch('sentinel.client.requests.post')
    def test_status_ok(self, mock_post, _mock_set, _mock_get):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {'access_token': 'tok', 'expires_in': 3600},
            raise_for_status=MagicMock(),
        )
        r = self.client.get('/api/v1/sentinel/status/')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data['ok'])

    def test_status_not_configured(self):
        with override_settings(SENTINEL_HUB_CLIENT_ID='', SENTINEL_HUB_CLIENT_SECRET=''):
            r = self.client.get('/api/v1/sentinel/status/')
        self.assertFalse(r.data['configured'])

    def test_layers_list(self):
        r = self.client.get('/api/v1/sentinel/layers/')
        self.assertEqual(r.status_code, 200)
        ids = [x['id'] for x in r.data['layers']]
        self.assertIn('ndvi', ids)
        self.assertIn('true_color', ids)

    @patch('sentinel.views.process_image', return_value=b'\x89PNG\r\n')
    def test_tile_png(self, _mock_proc):
        r = self.client.get('/api/v1/sentinel/tiles/ndvi/10/512/512.png')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'image/png')
