from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from accounts.social_models import UserFavorite, UserFollow
from videos.models import VideoPost


class SocialAPITest(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice',
            password='pass12345',
            role=User.Role.PUBLIC,
        )
        self.bob = User.objects.create_user(
            username='bob',
            password='pass12345',
            role=User.Role.PUBLIC,
        )
        VideoPost.objects.create(
            author=self.alice,
            kind=VideoPost.Kind.VIDEO,
            title='Alice vidéo',
            file=SimpleUploadedFile('a.mp4', b'x', content_type='video/mp4'),
            status=VideoPost.Status.PUBLISHED,
        )

    def test_follow_and_feed(self):
        self.client.force_authenticate(self.bob)
        res = self.client.post(reverse('auth-user-follow', kwargs={'username': 'alice'}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(UserFollow.objects.filter(
            follower=self.bob, following=self.alice,
        ).exists())
        feed = self.client.get(reverse('auth-feed'))
        self.assertEqual(feed.status_code, status.HTTP_200_OK)
        self.assertEqual(len(feed.data['results']), 1)
        self.client.delete(reverse('auth-user-follow', kwargs={'username': 'alice'}))
        self.assertFalse(UserFollow.objects.filter(
            follower=self.bob, following=self.alice,
        ).exists())

    def test_public_profile_and_search(self):
        res = self.client.get(reverse('auth-user-public', kwargs={'username': 'alice'}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['stats']['videos'], 1)
        search = self.client.get(reverse('auth-users-search'), {'q': 'ali'})
        self.assertEqual(search.status_code, status.HTTP_200_OK)
        self.assertTrue(any(r['username'] == 'alice' for r in search.data['results']))

    def test_favorites(self):
        post = VideoPost.objects.get(author=self.alice)
        self.client.force_authenticate(self.bob)
        add = self.client.post(
            reverse('auth-favorites'),
            {'target_type': 'video', 'target_id': post.pk},
            format='json',
        )
        self.assertIn(add.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))
        lst = self.client.get(reverse('auth-favorites'))
        self.assertEqual(len(lst.data['results']), 1)
        self.client.delete(
            reverse('auth-favorites'),
            {'target_type': 'video', 'target_id': post.pk},
            format='json',
        )
        self.assertFalse(UserFavorite.objects.filter(user=self.bob).exists())
