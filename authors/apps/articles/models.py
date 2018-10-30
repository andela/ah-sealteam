"""
Imports
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from ..authentication.models import User
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class TaggedItem(models.Model):
    """
    Tags arbitrary model instances using generic relation
    """
    tag_name = models.SlugField()
    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    tagged_object = GenericForeignKey('content_type', 'object_id')

    objects = models.Manager()

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self):
        return self.tag_name

class Article(models.Model):
    """
    When a user registers in the application, this class create the models for
    what the user will do once they have an account and that is post an article
    The class creates the models for the functionality.
    """
    author = models.ForeignKey(User, related_name='article', blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=250, unique=True)
    body = models.TextField(max_length=500, unique=True)
    tags = GenericRelation(TaggedItem)
    createdAt = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()
    updatedAt = models.DateField(blank=True, null=True)
    favorited = models.BooleanField(default=False)

    objects = models.Manager()

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title
