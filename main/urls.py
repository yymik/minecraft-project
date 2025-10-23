from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("notice/", views.notice, name="notice"),
    path("tutorial/", views.tutorial, name="tutorial"),
    path("discussion/", views.discussion, name="discussion"),
    path("history/", views.history, name="history"),
]
