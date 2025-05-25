# enchant_recommender/urls.py
from django.urls import path
from . import views

app_name = 'enchant_recommender'

urlpatterns = [
    path('', views.recommender_view, name='recommender'),
]