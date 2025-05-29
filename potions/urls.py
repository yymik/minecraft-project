from django.urls import path
from . import views

app_name = 'potions'

urlpatterns = [
    path('simulator/', views.potion_simulator_view, name='simulator'),
]
