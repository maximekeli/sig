from rest_framework import serializers

from .models import PedagogicalSheet, QuizQuestion, QuizSession, UserBadge


class PedagogicalSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedagogicalSheet
        fields = '__all__'


class QuizQuestionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ('id', 'text', 'difficulty', 'choices', 'points', 'is_nasa_topic')


class QuizAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_index = serializers.IntegerField(min_value=0, max_value=3)


class QuizSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSession
        fields = '__all__'
        read_only_fields = ('user', 'score', 'questions_answered', 'completed', 'started_at', 'finished_at')


class UserBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBadge
        fields = ('badge', 'earned_at')
