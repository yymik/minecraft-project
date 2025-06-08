<<<<<<< HEAD
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
=======
# accounts/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 로그인 URL -> views.py의 login_view 함수를 찾음
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('send-otp/', views.send_otp_view, name='send_otp'),
    
]
>>>>>>> 1756a89 (0608 15:51 json 스킨편집기)
