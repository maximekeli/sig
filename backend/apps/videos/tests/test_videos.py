from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from videos.models import VideoPost


class VideoPostAPITest(APITestCase):
    def setUp(self):
        self.public = User.objects.create_user(
            username='vid_public',
            password='pass12345',
            role=User.Role.PUBLIC,
        )
        self.admin = User.objects.create_user(
            username='vid_admin',
            password='pass12345',
            role=User.Role.ADMIN,
        )
        self.video_file = SimpleUploadedFile(
            'clip.mp4',
            b'fake-video-bytes',
            content_type='video/mp4',
        )

    def _url(self, name, **kwargs):
        return reverse(name, kwargs=kwargs)

    def test_public_upload_pending(self):
        self.client.force_authenticate(self.public)
        res = self.client.post(
            self._url('video-post-list'),
            {
                'kind': 'video',
                'title': 'Mon terrain',
                'description': 'Sol argileux',
                'file': self.video_file,
            },
            format='multipart',
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'pending')

    def test_admin_upload_published(self):
        self.client.force_authenticate(self.admin)
        res = self.client.post(
            self._url('video-post-list'),
            {
                'kind': 'short',
                'title': 'Short admin',
                'file': SimpleUploadedFile(
                    's.mp4', b'x', content_type='video/mp4',
                ),
                'duration_seconds': 30,
            },
            format='multipart',
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'published')

    def test_anon_lists_only_published(self):
        VideoPost.objects.create(
            author=self.public,
            kind=VideoPost.Kind.VIDEO,
            title='Pending',
            file=SimpleUploadedFile('a.mp4', b'1', content_type='video/mp4'),
            status=VideoPost.Status.PENDING,
        )
        VideoPost.objects.create(
            author=self.admin,
            kind=VideoPost.Kind.VIDEO,
            title='Live',
            file=SimpleUploadedFile('b.mp4', b'2', content_type='video/mp4'),
            status=VideoPost.Status.PUBLISHED,
        )
        res = self.client.get(self._url('video-post-list'), {'kind': 'video'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [r['title'] for r in res.data['results']]
        self.assertEqual(titles, ['Live'])

    def test_admin_approve(self):
        post = VideoPost.objects.create(
            author=self.public,
            kind=VideoPost.Kind.SHORT,
            title='A modérer',
            file=SimpleUploadedFile('c.mp4', b'3', content_type='video/mp4'),
            status=VideoPost.Status.PENDING,
        )
        self.client.force_authenticate(self.admin)
        res = self.client.post(self._url('video-post-approve', pk=post.pk))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.status, VideoPost.Status.PUBLISHED)
