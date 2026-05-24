"""Tests unitaires — client Sentinel Hub (sans appel réseau)."""
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase, override_settings

from sentinel.client import (
    SentinelHubError,
    clip_bbox_to_region,
    get_access_token,
    has_secret,
    is_configured,
    process_image,
    tile_xyz_to_bbox,
)


@override_settings(
    SENTINEL_HUB_CLIENT_ID='cid',
    SENTINEL_HUB_CLIENT_SECRET='csecret',
    SENTINEL_HUB_TOKEN_URL='https://auth.example/token',
    REGION_MARITIME_BBOX=(0.9, 6.0, 1.8, 6.8),
)
class SentinelClientTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_is_configured_and_has_secret(self):
        self.assertTrue(is_configured())
        self.assertTrue(has_secret())

    @override_settings(SENTINEL_HUB_CLIENT_ID='')
    def test_not_configured_without_client_id(self):
        self.assertFalse(is_configured())
        self.assertTrue(has_secret())

    @patch('sentinel.client.requests.post')
    def test_get_access_token_caches(self, mock_post):
        mock_post.return_value = MagicMock(
            ok=True,
            status_code=200,
            json=lambda: {'access_token': 'abc123', 'expires_in': 3600},
            raise_for_status=MagicMock(),
        )
        t1 = get_access_token()
        t2 = get_access_token()
        self.assertEqual(t1, 'abc123')
        self.assertEqual(t2, 'abc123')
        mock_post.assert_called_once()

    @patch('sentinel.client.requests.post')
    def test_get_access_token_oauth_error(self, mock_post):
        mock_post.return_value = MagicMock(
            ok=False,
            status_code=401,
            text='invalid_client',
        )
        with self.assertRaises(SentinelHubError) as ctx:
            get_access_token(force_refresh=True)
        self.assertIn('401', str(ctx.exception))

    def test_clip_bbox_to_region(self):
        inside = (1.0, 6.1, 1.5, 6.5)
        clipped = clip_bbox_to_region(inside, (0.9, 6.0, 1.8, 6.8))
        self.assertEqual(clipped, inside)

    def test_clip_bbox_outside_returns_none(self):
        outside = (5.0, 10.0, 6.0, 11.0)
        self.assertIsNone(clip_bbox_to_region(outside, (0.9, 6.0, 1.8, 6.8)))

    def test_tile_xyz_to_bbox_order(self):
        bbox = tile_xyz_to_bbox(10, 512, 512)
        self.assertEqual(len(bbox), 4)
        min_lon, min_lat, max_lon, max_lat = bbox
        self.assertLess(min_lon, max_lon)
        self.assertLess(min_lat, max_lat)

    def test_process_image_unknown_layer(self):
        with self.assertRaises(SentinelHubError) as ctx:
            process_image('invalid_layer', (1.0, 6.1, 1.2, 6.3))
        self.assertIn('inconnue', str(ctx.exception).lower())

    @patch('sentinel.client.get_access_token', return_value='tok')
    @patch('sentinel.client.requests.post')
    def test_process_image_success(self, mock_post, _mock_token):
        mock_post.return_value = MagicMock(
            status_code=200,
            content=b'\x89PNG',
            raise_for_status=MagicMock(),
            ok=True,
        )
        data = process_image('ndvi', (1.1, 6.2, 1.3, 6.4), width=64, height=64)
        self.assertEqual(data, b'\x89PNG')
        call_kwargs = mock_post.call_args
        self.assertIn('Bearer tok', call_kwargs.kwargs['headers']['Authorization'])


@override_settings(
    SENTINEL_HUB_CLIENT_ID='test-client-id',
    SENTINEL_HUB_CLIENT_SECRET='test-secret',
    REGION_MARITIME_BBOX=(0.9, 6.0, 1.8, 6.8),
)
class SentinelHubAPITest(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient

        self.client = APIClient()
        cache.clear()

    @patch('sentinel.client.requests.post')
    def test_status_ok(self, mock_post):
        mock_post.return_value = MagicMock(
            ok=True,
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

    @override_settings(
        SENTINEL_HUB_CLIENT_ID='',
        SENTINEL_HUB_CLIENT_SECRET='only-secret',
    )
    def test_status_secret_without_client_id(self):
        r = self.client.get('/api/v1/sentinel/status/')
        self.assertFalse(r.data['ok'])
        self.assertTrue(r.data.get('has_secret'))
        self.assertIn('CLIENT_ID', r.data['message'])

    def test_layers_list(self):
        r = self.client.get('/api/v1/sentinel/layers/')
        self.assertEqual(r.status_code, 200)
        ids = [x['id'] for x in r.data['layers']]
        self.assertIn('ndvi', ids)
        self.assertIn('true_color', ids)

    @patch('sentinel.views.ndvi_mean_for_bbox', return_value={
        'ndvi_mean': 0.42,
        'ndvi_min': 0.2,
        'ndvi_max': 0.6,
        'pixel_count': 100,
        'period': {'from': '2026-01-01T00:00:00Z', 'to': '2026-05-01T00:00:00Z'},
    })
    def test_analyze_bbox(self, _mock_ndvi):
        r = self.client.post(
            '/api/v1/sentinel/analyze/',
            {'bbox': '1.0,6.1,1.3,6.4'},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        self.assertAlmostEqual(r.data['ndvi_mean'], 0.42)

    def test_analyze_bbox_outside_region(self):
        r = self.client.post(
            '/api/v1/sentinel/analyze/',
            {'bbox': '10.0,10.0,11.0,11.0'},
            format='json',
        )
        self.assertEqual(r.status_code, 400)

    @patch('sentinel.views.clip_bbox_to_region', return_value=None)
    def test_tile_outside_region_204(self, _mock_clip):
        r = self.client.get('/api/v1/sentinel/tiles/ndvi/5/10/10.png')
        self.assertEqual(r.status_code, 204)

    @patch('sentinel.views.clip_bbox_to_region', return_value=(1.0, 6.1, 1.2, 6.3))
    @patch('sentinel.views.process_image', return_value=b'\x89PNG\r\n')
    def test_tile_png(self, _mock_proc, _mock_clip):
        r = self.client.get('/api/v1/sentinel/tiles/ndvi/11/1032/720.png')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'image/png')
