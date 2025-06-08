# skin_editor/urls.py

from django.urls import path
from . import views

app_name = 'skin_editor'  # URL 네임스페이스 설정 (권장)

urlpatterns = [
    path('', views.editor_page_view, name='editor_page'), # 스킨 편집기 메인 페이지
    path('api/get-skin/', views.get_skin_api_view, name='get_skin_api'), # 스킨 데이터 가져오는 API (프록시)
]