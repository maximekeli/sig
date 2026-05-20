from rest_framework import serializers

from .models import PedagogicalSheet, QuizQuestion, QuizSession, UserBadge


class PedagogicalSheetSerializer(serializers.ModelSerializer):
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = PedagogicalSheet
        fields = ('id', 'title', 'theme', 'content_fr', 'pdf_url', 'video_url', 'order')

    def get_pdf_url(self, obj):
        request = self.context.get('request')
        rel = f'/api/v1/education/sheets/{obj.pk}/pdf/'
        if request:
            return request.build_absolute_uri(rel)
        return rel


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
