from django.db import models
from django.contrib.auth.models import User

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_tokens")
    token = models.CharField(max_length=255, unique=True, db_index=True)
    purpose = models.CharField(max_length=32, default="verify_email")
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}:{self.purpose}:{'used' if self.used else 'new'}"
