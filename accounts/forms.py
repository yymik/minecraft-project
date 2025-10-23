from django import forms
from django.contrib.auth.models import User
import re
from .models import UserProfile

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    minecraft_uuid = forms.CharField(max_length=36, label="Minecraft UUID", 
                                   help_text="Minecraft UUID를 입력하세요 (32자리 또는 하이픈 포함 36자리)")
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

    def clean_minecraft_uuid(self):
        uuid = self.cleaned_data.get("minecraft_uuid", "").strip()
        if not uuid:
            raise forms.ValidationError("Minecraft UUID를 입력해주세요.")
        
        # UUID 형식 검증 (32자리 또는 하이픈 포함 36자리)
        uuid_pattern = r'^[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}$'
        if not re.match(uuid_pattern, uuid):
            raise forms.ValidationError("올바른 Minecraft UUID 형식이 아닙니다.")
        
        # 하이픈 제거하여 32자리로 정규화
        normalized_uuid = uuid.replace('-', '')
        
        # 중복 검사
        if UserProfile.objects.filter(minecraft_uuid__in=[uuid, normalized_uuid]).exists():
            raise forms.ValidationError("이미 사용 중인 Minecraft UUID입니다.")
        
        return normalized_uuid

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
