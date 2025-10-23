from django.urls import path
from .views import chat_view, user_info_view

urlpatterns = [
    path('chat/', chat_view, name='chat'),
    path('user-info/', user_info_view, name='user_info'),
]
