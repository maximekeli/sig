from django.conf import settings
from django.db import models


def video_upload_to(instance, filename):
    from django.utils import timezone

    sub = timezone.now().strftime('%Y/%m')
    folder = 'shorts' if instance.kind == VideoPost.Kind.SHORT else 'videos'
    return f'{folder}/{sub}/{filename}'


class VideoPost(models.Model):
    """Publication vidéo (long format) ou short (format court)."""

    class Kind(models.TextChoices):
        VIDEO = 'video', 'Vidéo'
        SHORT = 'short', 'Short'

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        PUBLISHED = 'published', 'Publié'
        REJECTED = 'rejected', 'Refusé'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='video_posts',
    )
    kind = models.CharField(max_length=10, choices=Kind.choices, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=video_upload_to)
    thumbnail = models.ImageField(
        upload_to='videos/thumbnails/%Y/%m/',
        blank=True,
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    duration_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Durée indiquée par l’auteur (shorts ≤ 60 s recommandé)',
    )
    view_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(
        default=False,
        help_text='Mise en avant par un administrateur',
    )
    rejection_reason = models.TextField(blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='moderated_videos',
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Publication vidéo'
        verbose_name_plural = 'Publications vidéo'
        indexes = [
            models.Index(fields=['kind', 'status', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return f'{self.get_kind_display()}: {self.title}'
