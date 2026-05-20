from django.db.models import F, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from accounts.models import User

from .models import VideoPost
from .permissions import VideoPostPermission
from .serializers import VideoPostCreateSerializer, VideoPostSerializer


class VideoPostViewSet(viewsets.ModelViewSet):
    """Publications vidéo et shorts — upload, lecture, modération admin."""

    permission_classes = [VideoPostPermission]
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['kind', 'status', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'view_count']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return VideoPostCreateSerializer
        return VideoPostSerializer

    def get_queryset(self):
        qs = VideoPost.objects.select_related('author')
        user = self.request.user
        if isinstance(user, User) and user.is_authenticated:
            if user.is_administrator:
                return qs
            return qs.filter(
                Q(status=VideoPost.Status.PUBLISHED) | Q(author=user),
            )
        return qs.filter(status=VideoPost.Status.PUBLISHED)

    def perform_create(self, serializer):
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == VideoPost.Status.PUBLISHED:
            VideoPost.objects.filter(pk=instance.pk).update(
                view_count=F('view_count') + 1,
            )
            instance.refresh_from_db(fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        post = self.get_object()
        post.status = VideoPost.Status.PUBLISHED
        post.rejection_reason = ''
        post.moderated_by = request.user
        post.moderated_at = timezone.now()
        post.save(
            update_fields=[
                'status', 'rejection_reason', 'moderated_by',
                'moderated_at', 'updated_at',
            ],
        )
        return Response(self.get_serializer(post).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        post = self.get_object()
        reason = (request.data.get('reason') or '').strip()[:500]
        post.status = VideoPost.Status.REJECTED
        post.rejection_reason = reason or 'Contenu non conforme.'
        post.moderated_by = request.user
        post.moderated_at = timezone.now()
        post.save(
            update_fields=[
                'status', 'rejection_reason', 'moderated_by',
                'moderated_at', 'updated_at',
            ],
        )
        return Response(self.get_serializer(post).data)

    @action(detail=True, methods=['post'])
    def feature(self, request, pk=None):
        post = self.get_object()
        post.is_featured = bool(request.data.get('featured', True))
        post.save(update_fields=['is_featured', 'updated_at'])
        return Response(self.get_serializer(post).data)

    @action(detail=False, methods=['get'], url_path='pending')
    def pending_list(self, request):
        """Liste des publications en attente (admin)."""
        if not request.user.is_administrator:
            return Response({'detail': 'Accès réservé aux administrateurs.'}, status=403)
        qs = VideoPost.objects.filter(
            status=VideoPost.Status.PENDING,
        ).select_related('author').order_by('-created_at')
        page = self.paginate_queryset(qs)
        ser = VideoPostSerializer(
            page if page is not None else qs,
            many=True,
            context={'request': request},
        )
        if page is not None:
            return self.get_paginated_response(ser.data)
        return Response(ser.data)
