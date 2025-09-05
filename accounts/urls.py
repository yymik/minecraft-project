# accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("verify/", views.verify_email_view, name="verify"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot/", views.forgot_password_view, name="forgot"),
    path("reset/<uidb64>/<token>/", views.reset_password_view, name="reset_password"),
    path("send-otp/", views.send_otp_view, name="send_otp"),
    path("verify-otp/", views.verify_otp_view, name="verify_otp"),
]
