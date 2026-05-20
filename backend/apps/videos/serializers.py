import os

from django.conf import settings
from rest_framework import serializers

from .models import VideoPost

ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.mkv', '.m4v'}
ALLOWED_THUMB_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def _ext(name):
    return os.path.splitext(name or '')[1].lower()


class VideoPostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_display = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    can_moderate = serializers.SerializerMethodField()

    class Meta:
        model = VideoPost
        fields = (
            'id', 'kind', 'title', 'description', 'status',
            'duration_seconds', 'view_count', 'is_featured',
            'author', 'author_username', 'author_display',
            'file_url', 'thumbnail_url', 'rejection_reason',
            'created_at', 'updated_at', 'can_moderate',
        )
        read_only_fields = (
            'id', 'status', 'view_count', 'author', 'author_username',
            'author_display', 'file_url', 'thumbnail_url',
            'rejection_reason', 'created_at', 'updated_at', 'can_moderate',
        )

    def get_author_display(self, obj):
        return obj.author.get_full_name() or obj.author.username

    def get_file_url(self, obj):
        return obj.file.url if obj.file else None

    def get_thumbnail_url(self, obj):
        return obj.thumbnail.url if obj.thumbnail else None

    def get_can_moderate(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        return bool(
            user
            and getattr(user, 'is_authenticated', False)
            and user.is_administrator
        )


class VideoPostCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    thumbnail = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = VideoPost
        fields = (
            'kind', 'title', 'description', 'file', 'thumbnail',
            'duration_seconds',
        )

    def validate_kind(self, value):
        if value not in (VideoPost.Kind.VIDEO, VideoPost.Kind.SHORT):
            raise serializers.ValidationError('Type invalide.')
        return value

    def validate_file(self, file_obj):
        ext = _ext(file_obj.name)
        if ext not in ALLOWED_VIDEO_EXTENSIONS:
            raise serializers.ValidationError(
                'Format vidéo non supporté (mp4, webm, mov, mkv, m4v).',
            )
        max_bytes = getattr(settings, 'VIDEO_MAX_UPLOAD_BYTES', 50 * 1024 * 1024)
        if file_obj.size > max_bytes:
            mb = max_bytes // (1024 * 1024)
            raise serializers.ValidationError(
                f'Fichier trop volumineux (max {mb} Mo).',
            )
        return file_obj

    def validate_thumbnail(self, thumb):
        if not thumb:
            return thumb
        if _ext(thumb.name) not in ALLOWED_THUMB_EXTENSIONS:
            raise serializers.ValidationError(
                'Miniature : jpg, png ou webp uniquement.',
            )
        return thumb

    def validate(self, attrs):
        kind = attrs.get('kind')
        duration = attrs.get('duration_seconds')
        if kind == VideoPost.Kind.SHORT and duration and duration > 60:
            raise serializers.ValidationError({
                'duration_seconds': 'Un short ne doit pas dépasser 60 secondes.',
            })
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        auto_publish = user.is_administrator or user.is_agent
        validated_data['author'] = user
        validated_data['status'] = (
            VideoPost.Status.PUBLISHED
            if auto_publish
            else VideoPost.Status.PENDING
        )
        return super().create(validated_data)
