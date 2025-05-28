from django.urls import path
from . import views
from .views import wiki_detail_view, wiki_edit_view

app_name = 'wiki'

urlpatterns = [
    path('', views.home, name='home'),
    path('<str:title>/', wiki_detail_view, name='wiki_detail'),
    path('<str:title>/edit', wiki_edit_view, name='wiki_edit'),
]
