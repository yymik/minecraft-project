from django.contrib import admin
from django.urls import path, include

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
]
