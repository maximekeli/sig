from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import UserLocation

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'organization', 'phone', 'pseudonym', 'date_joined',
        )
        read_only_fields = ('id', 'date_joined')


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'organization', 'pseudonym')

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role', User.Role.PUBLIC)
        if role == User.Role.ADMIN:
            validated_data['role'] = User.Role.PUBLIC
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLocationUpdateSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lon = serializers.FloatField(min_value=-180, max_value=180)
    accuracy_m = serializers.FloatField(required=False, allow_null=True, min_value=0)
    heading = serializers.FloatField(required=False, allow_null=True, min_value=0, max_value=360)
    is_sharing = serializers.BooleanField(required=False, default=True)


class UserLocationSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.CharField(source='user.display_name', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    lat = serializers.SerializerMethodField()
    lon = serializers.SerializerMethodField()

    class Meta:
        model = UserLocation
        fields = (
            'user_id', 'username', 'display_name', 'role',
            'lat', 'lon', 'accuracy_m', 'heading', 'is_sharing', 'updated_at',
        )

    def get_lat(self, obj):
        return obj.location.y

    def get_lon(self, obj):
        return obj.location.x


class UserLocationGeoSerializer(GeoFeatureModelSerializer):
    display_name = serializers.CharField(source='user.display_name', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = UserLocation
        geo_field = 'location'
        fields = (
            'user', 'display_name', 'role',
            'accuracy_m', 'heading', 'is_sharing', 'updated_at',
        )
