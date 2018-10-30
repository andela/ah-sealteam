"""
Imports
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from ..authentication.models import User
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class Article(models.Model):
    """
    When a user registers in the application, this class create the models for
    what the user will do once they have an account and that is post an article
    The class creates the models for the functionality.
    """
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    body = models.TextField(max_length=500)
    tags = GenericRelation(ContentType)
    createdAt = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()
    updatedAt = models.DateField(blank=True, null=True)
    favorited = models.BooleanField(default=False)
    author = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)

    class Meta:
        ordering = ('title')

    def __str__(self):
        return self.title

