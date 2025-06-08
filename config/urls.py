from django.contrib import admin
from django.urls import path, include
from main import views as main_views  # ← main 앱에 home_view가 있는 경우 기준

urlpatterns = [
    path('', main_views.home_view, name='home'),  # / => home.html 위키 대문 통합 구조
    path('admin/', admin.site.urls),
    path('main/', include('main.urls')),  # 필요 시 유지, but 메인 역할은 위에서 함
    path('accounts/', include('accounts.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('potions/', include('potions.urls')),
    path('enchant-recommender/', include('enchant_recommender.urls')),
    path('wiki/', include(('wiki.urls', 'wiki'), namespace='wiki')),  # 개별 문서/편집용
<<<<<<< HEAD
=======
    path('skin-editor/', include('skin_editor.urls')),
    path('save-analyzer/', include('save_analyzer.urls')), 
>>>>>>> 1756a89 (0608 15:51 json 스킨편집기)
]
