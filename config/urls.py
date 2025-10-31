from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from accounts.api_views import AuthTokenView, RegisterView
from chatbot.api_views import ChatbotMessageView
from wiki.api_views import WikiListView, WikiDetailView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 홈/공지/튜토/토론/역사 등은 main.urls가 전부 담당
    path('', include(('main.urls', 'main'), namespace='main')),

    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('chatbot/', include(('chatbot.urls', 'chatbot'), namespace='chatbot')),
    path('potions/', include(('potions.urls', 'potions'), namespace='potions')),
    path('enchant-recommender/', include(('enchant_recommender.urls', 'enchant_recommender'),
                                         namespace='enchant_recommender')),
    path('wiki/', include(('wiki.urls', 'wiki'), namespace='wiki')),
    path('skin-editor/', include(('skin_editor.urls', 'skin_editor'), namespace='skin_editor')),
    path('save-analyzer/', include(('save_analyzer.urls', 'save_analyzer'), namespace='save_analyzer')),

    path('api/auth/login/', AuthTokenView.as_view(), name='api-auth-login'),
    path('api/auth/register/', RegisterView.as_view(), name='api-auth-register'),
    path('api/chatbot/messages/', ChatbotMessageView.as_view(), name='api-chatbot-messages'),
    path('api/wiki/', WikiListView.as_view(), name='api-wiki-list'),
    path('api/wiki/<str:title>/', WikiDetailView.as_view(), name='api-wiki-detail'),
]

#wiki 이미지 서빙 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)