from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdministrator
from accounts.serializers import UserSerializer
from accounts.social_models import UserFavorite, UserFollow
from education.models import PedagogicalSheet, UserBadge
from education.serializers import UserBadgeSerializer
from sig_platform.notify import notify_user
from videos.models import VideoPost
from videos.serializers import VideoPostSerializer
from videos.services import annotate_post_engagement

User = get_user_model()


def _public_user_payload(user, request):
    from videos.models import VideoPost

    published = VideoPost.objects.filter(
        author=user,
        status=VideoPost.Status.PUBLISHED,
    )
    badges = UserBadge.objects.filter(user=user)
    follower_count = UserFollow.objects.filter(following=user).count()
    following_count = UserFollow.objects.filter(follower=user).count()
    me = request.user if request.user.is_authenticated else None
    is_following = False
    if me and me.pk != user.pk:
        is_following = UserFollow.objects.filter(
            follower=me, following=user,
        ).exists()
    return {
        'user': UserSerializer(user).data,
        'badges': UserBadgeSerializer(badges, many=True).data,
        'stats': {
            'videos': published.filter(kind=VideoPost.Kind.VIDEO).count(),
            'shorts': published.filter(kind=VideoPost.Kind.SHORT).count(),
            'followers': follower_count,
            'following': following_count,
        },
        'is_following': is_following,
        'is_self': me.pk == user.pk if me else False,
    }


class PublicProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        payload = _public_user_payload(user, request)
        qs = annotate_post_engagement(
            VideoPost.objects.filter(
                author=user,
                status=VideoPost.Status.PUBLISHED,
            ).select_related('author'),
            request.user,
        )
        payload['posts'] = VideoPostSerializer(
            qs[:50], many=True, context={'request': request},
        ).data
        return Response(payload)


class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        target = get_object_or_404(User, username=username)
        if target.pk == request.user.pk:
            return Response({'detail': 'Vous ne pouvez pas vous suivre vous-même.'}, status=400)
        _, created = UserFollow.objects.get_or_create(
            follower=request.user,
            following=target,
        )
        if created:
            notify_user(
                target,
                'Nouvel abonné',
                f'{request.user.username} vous suit maintenant.',
                link=f'/?view=profile&user={request.user.username}',
            )
        return Response({'following': True, 'created': created})

    def delete(self, request, username):
        target = get_object_or_404(User, username=username)
        UserFollow.objects.filter(
            follower=request.user,
            following=target,
        ).delete()
        return Response({'following': False})


class FollowingFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        following_ids = UserFollow.objects.filter(
            follower=request.user,
        ).values_list('following_id', flat=True)
        qs = annotate_post_engagement(
            VideoPost.objects.filter(
                author_id__in=following_ids,
                status=VideoPost.Status.PUBLISHED,
            ).select_related('author').order_by('-created_at'),
            request.user,
        )[:100]
        return Response({
            'results': VideoPostSerializer(
                qs, many=True, context={'request': request},
            ).data,
        })


class FavoritesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = []
        for fav in UserFavorite.objects.filter(user=request.user)[:200]:
            entry = {
                'id': fav.id,
                'target_type': fav.target_type,
                'target_id': fav.target_id,
                'created_at': fav.created_at,
            }
            if fav.target_type == UserFavorite.TargetType.VIDEO:
                try:
                    post = VideoPost.objects.get(pk=fav.target_id)
                    entry['video'] = VideoPostSerializer(
                        post, context={'request': request},
                    ).data
                except VideoPost.DoesNotExist:
                    continue
            elif fav.target_type == UserFavorite.TargetType.SHEET:
                try:
                    sheet = PedagogicalSheet.objects.get(pk=fav.target_id)
                    entry['sheet'] = {
                        'id': sheet.id,
                        'title': sheet.title,
                        'theme': sheet.theme,
                    }
                except PedagogicalSheet.DoesNotExist:
                    continue
            items.append(entry)
        return Response({'results': items})

    def post(self, request):
        target_type = request.data.get('target_type')
        target_id = request.data.get('target_id')
        if target_type not in UserFavorite.TargetType.values:
            return Response({'detail': 'Type invalide.'}, status=400)
        fav, created = UserFavorite.objects.get_or_create(
            user=request.user,
            target_type=target_type,
            target_id=int(target_id),
        )
        return Response(
            {'id': fav.id, 'created': created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request):
        target_type = request.data.get('target_type')
        target_id = request.data.get('target_id')
        UserFavorite.objects.filter(
            user=request.user,
            target_type=target_type,
            target_id=target_id,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = (request.query_params.get('q') or '').strip()
        if len(q) < 2:
            return Response({'results': []})
        users = User.objects.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q),
            is_active=True,
        )[:20]
        return Response({
            'results': [
                {
                    'username': u.username,
                    'display_name': u.get_full_name() or u.username,
                    'profile_photo_url': (
                        u.profile_photo.url if u.profile_photo else None
                    ),
                }
                for u in users
            ],
        })
