from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .messaging_models import DirectMessage

User = get_user_model()


class DirectMessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        with_user = request.query_params.get('with')
        qs = DirectMessage.objects.filter(
            Q(sender=request.user) | Q(recipient=request.user),
        ).select_related('sender', 'recipient').order_by('-created_at')[:100]
        if with_user:
            qs = qs.filter(
                Q(sender__username=with_user, recipient=request.user)
                | Q(sender=request.user, recipient__username=with_user),
            )
        return Response({
            'messages': [
                {
                    'id': m.id,
                    'from': m.sender.username,
                    'to': m.recipient.username,
                    'text': m.text,
                    'is_read': m.is_read,
                    'is_mine': m.sender_id == request.user.pk,
                    'created_at': m.created_at,
                }
                for m in qs
            ],
        })

    def post(self, request):
        to_username = (request.data.get('to') or '').strip()
        text = (request.data.get('text') or '').strip()
        if not to_username or not text:
            return Response({'detail': 'Destinataire et message requis.'}, status=400)
        recipient = User.objects.filter(username=to_username, is_active=True).first()
        if not recipient:
            return Response({'detail': 'Utilisateur introuvable.'}, status=404)
        if recipient.pk == request.user.pk:
            return Response({'detail': 'Envoi à soi-même impossible.'}, status=400)
        msg = DirectMessage.objects.create(
            sender=request.user,
            recipient=recipient,
            text=text[:2000],
        )
        return Response({'id': msg.id}, status=status.HTTP_201_CREATED)
