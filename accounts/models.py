from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """사용자 프로필 모델 - Minecraft UUID 등 추가 정보 저장"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    minecraft_uuid = models.CharField(max_length=36, unique=True, null=True, blank=True, help_text="Minecraft UUID (32자리 또는 하이픈 포함 36자리)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.minecraft_uuid or 'No UUID'}"

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_tokens")
    token = models.CharField(max_length=255, unique=True, db_index=True)
    purpose = models.CharField(max_length=32, default="verify_email")
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}:{self.purpose}:{'used' if self.used else 'new'}"
