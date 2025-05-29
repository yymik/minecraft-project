from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    path('<str:title>/', views.wiki_detail_view, name='wiki_detail'),
    path('<str:title>/edit/', views.wiki_edit_view, name='wiki_edit'),
]