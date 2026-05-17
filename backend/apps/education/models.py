from django.conf import settings
from django.db import models


class PedagogicalSheet(models.Model):
    """≥5 thematic sheets including NASA topics."""

    class Theme(models.TextChoices):
        SOIL_IMPORTANCE = 'importance', 'Importance des sols'
        SOIL_TYPES = 'types', 'Types de sols au Togo'
        BEST_PRACTICES = 'practices', 'Bonnes pratiques'
        NASA_DATA = 'nasa', 'Comprendre les données NASA'
        EROSION = 'erosion', 'Érosion et dégradation'

    title = models.CharField(max_length=200)
    theme = models.CharField(max_length=30, choices=Theme.choices)
    content_fr = models.TextField()
    pdf_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class QuizQuestion(models.Model):
    class Difficulty(models.TextChoices):
        EASY = 'facile', 'Facile'
        MEDIUM = 'moyen', 'Moyen'
        HARD = 'difficile', 'Difficile'

    text = models.TextField()
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices)
    choices = models.JSONField(help_text='List of 4 choices')
    correct_index = models.PositiveSmallIntegerField()
    explanation = models.TextField()
    is_nasa_topic = models.BooleanField(default=False)
    points = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['difficulty', 'id']

    def save(self, *args, **kwargs):
        if not self.points:
            self.points = {self.Difficulty.EASY: 5, self.Difficulty.MEDIUM: 10, self.Difficulty.HARD: 15}.get(
                self.difficulty, 5
            )
        super().save(*args, **kwargs)


class QuizSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=20)
    score = models.PositiveIntegerField(default=0)
    questions_answered = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)


class UserBadge(models.Model):
    class BadgeType(models.TextChoices):
        APPRENTI = 'apprenti', 'Apprenti'
        CONNAISSEUR = 'connaisseur', 'Connaisseur'
        EXPERT = 'expert', 'Expert des sols'
        NASA_CHAMPION = 'nasa_champion', 'Champion NASA'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    badge = models.CharField(max_length=30, choices=BadgeType.choices)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')


class UserQuizProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_score = models.PositiveIntegerField(default=0)
    difficult_sessions_passed = models.PositiveIntegerField(default=0)
    nasa_questions_correct = models.PositiveIntegerField(default=0)
    nasa_questions_total = models.PositiveIntegerField(default=0)
