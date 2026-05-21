from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0002_comments_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='videopost',
            name='category',
            field=models.CharField(
                choices=[
                    ('sols', 'Sols & agriculture'),
                    ('nasa', 'NASA & satellite'),
                    ('sig', 'SIG & cartographie'),
                    ('formation', 'Formation'),
                    ('autre', 'Autre'),
                ],
                db_index=True,
                default='sols',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='videocomment',
            name='is_hidden',
            field=models.BooleanField(
                default=False,
                help_text='Masqué par modération admin',
            ),
        ),
    ]
