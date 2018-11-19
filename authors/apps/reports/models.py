from django.db import models

from authors.apps.articles.models import Article
from django.contrib.auth import get_user_model


class Report(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        related_name='reporter',
        on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        Article,
        related_name='reported',
        on_delete=models.CASCADE
    )
    reason = models.TextField(max_length=700)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at', 'updated_at',)
        unique_together = ('user', 'article')

    def __str__(self):
        return self.user.username
