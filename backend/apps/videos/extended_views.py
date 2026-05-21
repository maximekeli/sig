from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdministrator
from .models import StoryPost, VideoComment
from .serializers import VideoPostSerializer


class StoryViewSet(viewsets.ModelViewSet):
    """Stories éphémères (24 h)."""

    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        return StoryPost.objects.filter(
            created_at__gte=cutoff,
        ).select_related('author').order_by('-created_at')

    def get_serializer_class(self):
        return VideoPostSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = [
            {
                'id': s.id,
                'author': s.author.username,
                'author_display': s.author.get_full_name() or s.author.username,
                'media_url': s.media.url if s.media else None,
                'caption': s.caption,
                'expires_at': s.expires_at,
                'created_at': s.created_at,
            }
            for s in qs[:50]
        ]
        return Response(data)

    def create(self, request, *args, **kwargs):
        media = request.FILES.get('media')
        if not media:
            return Response({'detail': 'Fichier média requis.'}, status=400)
        story = StoryPost.objects.create(
            author=request.user,
            media=media,
            caption=(request.data.get('caption') or '')[:500],
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )
        return Response({'id': story.id}, status=status.HTTP_201_CREATED)


def ai_moderation_hint(text: str) -> dict:
    """Heuristique simple (sans API externe) pour suggestion modération."""
    lower = (text or '').lower()
    flags = []
    blocked = ['spam', 'arnaque', 'haine', 'insulte']
    for w in blocked:
        if w in lower:
            flags.append(w)
    return {
        'suggested_hide': len(flags) > 0,
        'flags': flags,
        'confidence': 0.7 if flags else 0.1,
    }

