from django.contrib.auth import get_user_model
from rest_framework import serializers

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
