# potions/urls.py
from django.urls import path
from . import views

app_name = 'potions' # 앱 네임스페이스 설정

urlpatterns = [
    path('simulator/', views.potion_simulator_view, name='simulator'),
    # 여기에 potions 앱의 다른 뷰와 URL을 추가할 수 있습니다.
    # 예를 들어, 특정 물약 상세 정보 페이지 등
    # path('potion/<str:potion_id>/', views.potion_detail_view, name='potion_detail'),
]