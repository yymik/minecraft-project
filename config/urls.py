from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('chatbot/', include('chatbot.urls')),
]

print("✅ accounts.urls connected")
