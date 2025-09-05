from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean_username(self):
        u = self.cleaned_data["username"]
        if User.objects.filter(username=u).exists():
            raise forms.ValidationError("이미 사용 중인 아이디입니다.")
        return u

    def clean_email(self):
        e = self.cleaned_data["email"]
        if User.objects.filter(email=e).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")
        return e

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password2"):
            self.add_error("password2", "비밀번호가 일치하지 않습니다.")
        return cleaned

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ForgotForm(forms.Form):
    email = forms.EmailField()

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("new_password") != cleaned.get("new_password2"):
            self.add_error("new_password2", "비밀번호가 일치하지 않습니다.")
        return cleaned
