from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class WikiPage(models.Model):
    title = models.CharField(max_length=200, unique=True)
    content = models.TextField()
    summary = models.TextField(blank=True, help_text="문서 요약")
    category = models.CharField(max_length=50, default='기타', help_text="카테고리 (광물, 블록, 아이템, 몹, 인챈트 등)")
    tags = models.CharField(max_length=500, blank=True, help_text="태그 (쉼표로 구분)")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text="추천 문서")
    
    def __str__(self):
        return self.title

    class Meta:
        app_label = 'wiki'
        ordering = ['-updated_at']

class WikiRevision(models.Model):
    page = models.ForeignKey(WikiPage, on_delete=models.CASCADE, related_name='revisions')
    content = models.TextField()
    summary = models.CharField(max_length=200, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class WikiLink(models.Model):
    """위키 문서 간의 링크 관계"""
    from_page = models.ForeignKey(WikiPage, on_delete=models.CASCADE, related_name='outgoing_links')
    to_page = models.ForeignKey(WikiPage, on_delete=models.CASCADE, related_name='incoming_links')
    link_text = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_page', 'to_page']

class WikiCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="HEX 색상 코드")
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome 아이콘 클래스")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Wiki Categories"