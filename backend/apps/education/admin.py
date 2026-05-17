from django.contrib import admin

from .models import PedagogicalSheet, QuizQuestion, QuizSession, UserBadge, UserQuizProfile


@admin.register(PedagogicalSheet)
class PedagogicalSheetAdmin(admin.ModelAdmin):
    list_display = ('title', 'theme', 'order')


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'difficulty', 'points', 'is_nasa_topic', 'is_active')
    list_filter = ('difficulty', 'is_nasa_topic')


admin.site.register(QuizSession)
admin.site.register(UserBadge)
admin.site.register(UserQuizProfile)
