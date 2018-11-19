"""
Imports
"""

from django.db import models
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article

class Highlight(models.Model):
    """
    Models for highlighting a text in an article body
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)
    startoffset = models.IntegerField(blank=True, null=True)
    endoffset = models.IntegerField(blank=True, null=True)
    highlighted = models.CharField(max_length=200, blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return "Hignlighted: {} and comment: {}".format(self.highlighted, self.comment)
