from django.db.models import F, Q
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User

from .models import VideoComment, VideoPost
from .permissions import VideoCommentPermission, VideoPostPermission
from .serializers import (
    VideoCommentSerializer,
    VideoPostCreateSerializer,
    VideoPostSerializer,
)
from .services import (
    annotate_comment_engagement,
    annotate_post_engagement,
    toggle_comment_like,
    toggle_post_like,
    user_can_view_post,
)


class VideoPostViewSet(viewsets.ModelViewSet):
    """Publications vidéo et shorts — upload, lecture, likes, commentaires."""

    permission_classes = [VideoPostPermission]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
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
                base = qs
            else:
                base = qs.filter(
                    Q(status=VideoPost.Status.PUBLISHED) | Q(author=user),
                )
        else:
            base = qs.filter(status=VideoPost.Status.PUBLISHED)
        return annotate_post_engagement(base, user)

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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_like(self, request, pk=None):
        post = self.get_object()
        if not user_can_view_post(post, request.user):
            return Response({'detail': 'Publication inaccessible.'}, status=403)
        liked, count = toggle_post_like(post, request.user)
        return Response({'liked': liked, 'like_count': count})

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comments(self, request, pk=None):
        post = self.get_object()
        if not user_can_view_post(post, request.user):
            return Response({'detail': 'Publication inaccessible.'}, status=403)

        if request.method == 'GET':
            qs = annotate_comment_engagement(
                VideoComment.objects.filter(post=post).select_related(
                    'author', 'parent',
                ),
                request.user,
            )
            ser = VideoCommentSerializer(
                qs, many=True, context={'request': request},
            )
            return Response(ser.data)

        ser = VideoCommentSerializer(
            data=request.data,
            context={'request': request},
        )
        ser.is_valid(raise_exception=True)
        parent = ser.validated_data.get('parent')
        comment = VideoComment.objects.create(
            post=post,
            author=request.user,
            parent=parent,
            text=ser.validated_data['text'],
        )
        out = annotate_comment_engagement(
            VideoComment.objects.filter(pk=comment.pk).select_related('author'),
            request.user,
        ).first()
        return Response(
            VideoCommentSerializer(out, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

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
        refreshed = self.get_queryset().filter(pk=post.pk).first()
        return Response(self.get_serializer(refreshed).data)

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
        refreshed = self.get_queryset().filter(pk=post.pk).first()
        return Response(self.get_serializer(refreshed).data)

    @action(detail=True, methods=['post'])
    def feature(self, request, pk=None):
        post = self.get_object()
        post.is_featured = bool(request.data.get('featured', True))
        post.save(update_fields=['is_featured', 'updated_at'])
        refreshed = self.get_queryset().filter(pk=post.pk).first()
        return Response(self.get_serializer(refreshed).data)

    @action(detail=False, methods=['get'], url_path='pending')
    def pending_list(self, request):
        if not request.user.is_administrator:
            return Response(
                {'detail': 'Accès réservé aux administrateurs.'},
                status=403,
            )
        qs = annotate_post_engagement(
            VideoPost.objects.filter(
                status=VideoPost.Status.PENDING,
            ).select_related('author').order_by('-created_at'),
            request.user,
        )
        page = self.paginate_queryset(qs)
        ser = VideoPostSerializer(
            page if page is not None else qs,
            many=True,
            context={'request': request},
        )
        if page is not None:
            return self.get_paginated_response(ser.data)
        return Response(ser.data)


class VideoCommentViewSet(
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Suppression et like sur commentaires."""

    permission_classes = [VideoCommentPermission]
    serializer_class = VideoCommentSerializer
    queryset = VideoComment.objects.select_related('post', 'author')

    def get_queryset(self):
        return annotate_comment_engagement(
            super().get_queryset(),
            self.request.user,
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_like(self, request, pk=None):
        comment = self.get_object()
        if not user_can_view_post(comment.post, request.user):
            return Response({'detail': 'Publication inaccessible.'}, status=403)
        liked, count = toggle_comment_like(comment, request.user)
        return Response({'liked': liked, 'like_count': count})
