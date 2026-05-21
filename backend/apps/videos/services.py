from django.db.models import BooleanField, Count, Exists, OuterRef, Value

from .models import VideoComment, VideoCommentLike, VideoPost, VideoPostLike


def annotate_post_engagement(queryset, user=None):
    """Compteurs likes / commentaires + liked_by_me sur les publications."""
    qs = queryset.annotate(
        like_count=Count('post_likes', distinct=True),
        comment_count=Count('comments', distinct=True),
    )
    if user and getattr(user, 'is_authenticated', False):
        qs = qs.annotate(
            liked_by_me=Exists(
                VideoPostLike.objects.filter(
                    post_id=OuterRef('pk'),
                    user_id=user.pk,
                ),
            ),
        )
    else:
        qs = qs.annotate(liked_by_me=Value(False, output_field=BooleanField()))
    return qs


def annotate_comment_engagement(queryset, user=None):
    qs = queryset.annotate(
        like_count=Count('comment_likes', distinct=True),
        reply_count=Count('replies', distinct=True),
    )
    if user and getattr(user, 'is_authenticated', False):
        qs = qs.annotate(
            liked_by_me=Exists(
                VideoCommentLike.objects.filter(
                    comment_id=OuterRef('pk'),
                    user_id=user.pk,
                ),
            ),
        )
    else:
        qs = qs.annotate(liked_by_me=Value(False, output_field=BooleanField()))
    return qs


def toggle_post_like(post: VideoPost, user) -> tuple[bool, int]:
    like, created = VideoPostLike.objects.get_or_create(post=post, user=user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    count = VideoPostLike.objects.filter(post=post).count()
    return liked, count


def toggle_comment_like(comment: VideoComment, user) -> tuple[bool, int]:
    like, created = VideoCommentLike.objects.get_or_create(
        comment=comment,
        user=user,
    )
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    count = VideoCommentLike.objects.filter(comment=comment).count()
    return liked, count


def user_can_view_post(post: VideoPost, user) -> bool:
    if post.status == VideoPost.Status.PUBLISHED:
        return True
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    return post.author_id == user.pk or user.is_administrator
