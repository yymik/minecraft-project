# enchant_recommender/models.py
from django.db import models
from django.contrib.auth.models import User
import json


class EnchantmentRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자")
    item_type = models.CharField(max_length=50, verbose_name="장비 종류")

    # 좋아요 개수를 저장할 필드 추가
    likes_count = models.IntegerField(default=0, verbose_name="좋아요 수")

    # JSONField를 사용하여 인챈트 ID 리스트를 저장
    recommended_enchants = models.JSONField(default=list, verbose_name="추천 인챈트 (ID)")
    general_enchants = models.JSONField(default=list, verbose_name="일반 인챈트 (ID)")
    not_recommended_enchants = models.JSONField(default=list, verbose_name="비추천 인챈트 (ID)")

    title = models.CharField(max_length=100, verbose_name="게시물 제목", default="")

    memo = models.TextField(blank=True, null=True, verbose_name="메모")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    def __str__(self):
        return f"{self.user.username} - {self.item_type} 추천 ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "인챈트 추천 게시물"
        verbose_name_plural = "인챈트 추천 게시물"

    def __str__(self):
        return f"{self.user.username} - {self.item_type} 추천 ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "인챈트 추천 게시물"
        verbose_name_plural = "인챈트 추천 게시물"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendation = models.ForeignKey(EnchantmentRecommendation, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 이 부분이 계정당 좋아요 제한을 구현합니다.
        unique_together = ('user', 'recommendation')