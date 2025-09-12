# save_analyzer/urls.py

from django.urls import path
from . import views

app_name = 'save_analyzer'

urlpatterns = [
    # '/save-analyzer/upload/' 주소에 대한 요청을
    # views.py의 upload_and_analyze_page 함수와 연결합니다.
    path('upload/', views.upload_and_analyze_page, name='upload_page'),
]