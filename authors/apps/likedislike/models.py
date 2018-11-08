"""
This module creates the model for like and dislike
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType

from authors.apps.authentication.models import User

class LikeDislikeManager(models.Manager):
    """
    Manager class for like and dislike
    """
    use_for_related_fields = True
 
    def likes(self):
        """
        get all the likes for an object
        """
        return self.get_queryset().filter(vote__gt=0)
 
    def dislikes(self):
        """
        get all the dislikes of an object
        """
        return self.get_queryset().filter(vote__lt=0)
 
    def sum_rating(self):
        """
        obtain the aggregate likes/dislikes
        """
        return self.get_queryset().aggregate(Sum('vote')).get('vote__sum') or 0

    def articles(self):
        """
        obtain the votes of a particular user to articles
        """
        return self.get_queryset().filter(content_type__model='article').order_by('-articles__published_at')

    def comments(self):
        """
        obtain the votes of a particular user to comments
        """
        return self.get_queryset().filter(content_type__model='comment').order_by('-comments__createdAt')

class LikeDislike(models.Model):
    """
    Users should be able to like and/or dislike an article or comment.
    This class creates the fields for like/dislike
    """
    LIKE = 1
    DISLIKE = -1
 
    VOTES = (
        (DISLIKE, 'Dislike'),
        (LIKE, 'Like')
    )
 
    vote = models.SmallIntegerField(verbose_name=_("vote"), choices=VOTES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    
    objects = LikeDislikeManager()

    def __str__(self):
        return "Vote: {}".format(self.vote)
