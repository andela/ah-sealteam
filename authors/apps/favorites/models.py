from django.db import models
# from authors.apps.articles.models import Article
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from authors.apps.authentication.models import User


class FavoriteManager(models.Manager):
    """
    Manager class for favoriting
    """
    # use_for_related_fields = True
 
    def favorites(self):
        """
        get all the favorites for an object
        """
        # import pdb;pdb.set_trace()
        return self.get_queryset()

class Favorite(models.Model):
    """
    Favorite model
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    object_id = models.PositiveIntegerField(null=True)
    article_object = GenericForeignKey('content_type', 'object_id')
    objects = FavoriteManager()

    class Meta:
        unique_together = (('user', 'object_id'),)
        ordering = ['-created_at']

    def __str__(self):
        """
        Method returns a string representation of a user and article
        """
        return "{} favorited by user {}".format(self.article_object, self.user)
