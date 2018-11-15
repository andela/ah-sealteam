"""
this module defines the models for the comments app
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.likedislike.models import LikeDislike
from simple_history.models import HistoricalRecords

class Comment(models.Model):
    parent = models.ForeignKey('self', null=True, blank=False, on_delete=models.CASCADE, related_name='thread')
    article = models.ForeignKey(Article, related_name='comment', null=True, blank=True, on_delete=models.CASCADE) 
    author = models.ForeignKey(User, related_name='comment', blank=True, null=True, on_delete=models.CASCADE)
    body = models.CharField(max_length=200)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    votes = GenericRelation(LikeDislike, related_query_name='comments')

    def __str__(self):
        return self.body

