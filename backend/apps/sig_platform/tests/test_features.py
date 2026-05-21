from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class PlatformFeaturesTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='feat_user',
            password='pass12345',
            role=User.Role.PUBLIC,
        )
        self.client.force_authenticate(self.user)

    def test_global_search_and_dashboard(self):
        r = self.client.get('/api/v1/platform/search/?q=sol')
        self.assertEqual(r.status_code, 200)
        self.assertIn('results', r.data)
        d = self.client.get('/api/v1/platform/me/dashboard/')
        self.assertEqual(d.status_code, 200)
        self.assertIn('videos', d.data)

    def test_notifications_unread(self):
        r = self.client.get('/api/v1/platform/notifications/unread-count/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('unread_count', r.data)
