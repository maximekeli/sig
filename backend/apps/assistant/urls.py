from django.urls import path

from .views import AssistantChatView, AssistantStatusView

urlpatterns = [
    path('status/', AssistantStatusView.as_view(), name='assistant-status'),
    path('chat/', AssistantChatView.as_view(), name='assistant-chat'),
]
