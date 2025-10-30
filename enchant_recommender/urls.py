# enchant_recommender/urls.py
from django.urls import path
from . import views

app_name = 'enchant_recommender'

urlpatterns = [
    path('', views.enchant_main_view, name='main'),  # 기본은 메인페이지
    path('recommender/', views.recommender_view, name='recommender'),  # 만들기 눌렀을 때
    path("like/", views.like_post, name="like_post"),
    path('list/', views.recommendation_list_view, name='list'),  # 게시물 목록
    path('<int:pk>/', views.recommendation_detail_view, name='detail'),  # 게시물 상세
    path('new/', views.start_new_recommendation_view, name='new_recommender'),
]