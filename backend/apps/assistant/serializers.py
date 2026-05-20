from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=('user', 'assistant'))
    content = serializers.CharField(max_length=8000)


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=4000)
    history = ChatMessageSerializer(many=True, required=False, default=list)
    context = serializers.JSONField(required=False, default=dict)

    def validate_message(self, value):
        text = value.strip()
        if not text:
            raise serializers.ValidationError('Message vide.')
        return text
