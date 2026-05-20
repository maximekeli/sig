from rest_framework import serializers

from .models import AuditLog, DroughtAlert, Notification, UserActivityEvent


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default='')

    class Meta:
        model = AuditLog
        fields = ('id', 'username', 'action', 'resource', 'resource_id', 'detail', 'created_at')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'level', 'link', 'is_read', 'created_at')


class DroughtAlertSerializer(serializers.ModelSerializer):
    soil_point_id = serializers.IntegerField(source='soil_point.id', read_only=True, allow_null=True)
    lat = serializers.SerializerMethodField()
    lon = serializers.SerializerMethodField()

    class Meta:
        model = DroughtAlert
        fields = (
            'id', 'soil_point_id', 'lat', 'lon', 'ndvi', 'smap',
            'severity', 'message', 'is_active', 'created_at',
        )

    def get_lat(self, obj):
        if obj.soil_point:
            return obj.soil_point.location.y
        return None

    def get_lon(self, obj):
        if obj.soil_point:
            return obj.soil_point.location.x
        return None


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Les mots de passe ne correspondent pas.',
            })
        return attrs


class ActivityEventInSerializer(serializers.Serializer):
    event_type = serializers.CharField(max_length=80)
    category = serializers.CharField(max_length=20, required=False, default='other')
    view_name = serializers.CharField(max_length=40, required=False, allow_blank=True)
    detail = serializers.DictField(required=False, default=dict)


class ActivityBatchSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=64)
    events = ActivityEventInSerializer(many=True)

    def validate_events(self, value):
        if len(value) > 100:
            raise serializers.ValidationError('Maximum 100 événements par lot.')
        if not value:
            raise serializers.ValidationError('Liste vide.')
        return value


class UserActivityEventSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default='')

    class Meta:
        model = UserActivityEvent
        fields = (
            'id', 'username', 'user', 'session_id', 'event_type', 'category',
            'view_name', 'detail', 'ip_address', 'created_at',
        )
