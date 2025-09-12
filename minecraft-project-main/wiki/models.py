from django.db import models

class WikiPage(models.Model):
    title = models.CharField(max_length=100, unique=True)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'wiki'