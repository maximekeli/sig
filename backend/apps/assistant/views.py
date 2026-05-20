from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from config.throttling import AssistantAnonThrottle, AssistantUserThrottle

from .serializers import ChatRequestSerializer
from .services.gemini import chat_with_gemini, is_available


class AssistantStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from django.conf import settings
        return Response({
            'available': is_available(),
            'model': getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash'),
        })


class AssistantChatView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AssistantAnonThrottle, AssistantUserThrottle]

    def post(self, request):
        ser = ChatRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        reply, err = chat_with_gemini(
            ser.validated_data['message'],
            history=ser.validated_data.get('history'),
            context=ser.validated_data.get('context'),
        )
        if err:
            code = status.HTTP_503_SERVICE_UNAVAILABLE
            if 'non configuré' in err.lower() or 'non installée' in err.lower():
                code = status.HTTP_503_SERVICE_UNAVAILABLE
            return Response({'error': err}, status=code)
        return Response({'reply': reply})
