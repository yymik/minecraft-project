from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('/main/')),
    path('admin/', admin.site.urls),
    path('main/', include('main.urls')),
    path('accounts/', include('accounts.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('potions/', include('potions.urls')),
    path('enchant-recommender/', include('enchant_recommender.urls')),
    path('wiki/', include('wiki.urls')),
]