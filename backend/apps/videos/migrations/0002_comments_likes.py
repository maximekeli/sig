import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=2000)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_comments', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='videos.videocomment')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='videos.videopost')),
            ],
            options={
                'verbose_name': 'Commentaire vidéo',
                'verbose_name_plural': 'Commentaires vidéo',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='VideoPostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_likes', to='videos.videopost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_post_likes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VideoCommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_likes', to='videos.videocomment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_comment_likes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='videocomment',
            index=models.Index(fields=['post', 'created_at'], name='videos_vide_post_id_6a8c2a_idx'),
        ),
        migrations.AddIndex(
            model_name='videocomment',
            index=models.Index(fields=['parent', 'created_at'], name='videos_vide_parent__b3f1e2_idx'),
        ),
        migrations.AddConstraint(
            model_name='videopostlike',
            constraint=models.UniqueConstraint(fields=('post', 'user'), name='videos_unique_post_like'),
        ),
        migrations.AddConstraint(
            model_name='videocommentlike',
            constraint=models.UniqueConstraint(fields=('comment', 'user'), name='videos_unique_comment_like'),
        ),
    ]
