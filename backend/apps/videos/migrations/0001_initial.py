import videos.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('video', 'Vidéo'), ('short', 'Short')], db_index=True, max_length=10)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('file', models.FileField(upload_to=videos.models.video_upload_to)),
                ('thumbnail', models.ImageField(blank=True, upload_to='videos/thumbnails/%Y/%m/')),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('published', 'Publié'), ('rejected', 'Refusé')], db_index=True, default='pending', max_length=12)),
                ('duration_seconds', models.PositiveIntegerField(blank=True, help_text='Durée indiquée par l’auteur (shorts ≤ 60 s recommandé)', null=True)),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('is_featured', models.BooleanField(default=False, help_text='Mise en avant par un administrateur')),
                ('rejection_reason', models.TextField(blank=True)),
                ('moderated_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_posts', to=settings.AUTH_USER_MODEL)),
                ('moderated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='moderated_videos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Publication vidéo',
                'verbose_name_plural': 'Publications vidéo',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='videopost',
            index=models.Index(fields=['kind', 'status', '-created_at'], name='videos_vide_kind_8a1f0d_idx'),
        ),
        migrations.AddIndex(
            model_name='videopost',
            index=models.Index(fields=['author', '-created_at'], name='videos_vide_author_2c8e91_idx'),
        ),
    ]
