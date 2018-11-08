"""

Serializer for like and dislike

"""
from rest_framework import serializers

from rest_framework.permissions import IsAuthenticatedOrReadOnly

# from authors.apps.articles.models import Article
from .models import LikeDislike

class VoteObjectRelatedSerializer(serializers.RelatedField):
    """
    A custom field to use for the votes generic relationship
    """
    def get_queryset(self):
        return LikeDislike.objects.all()

    def to_representation(self, value):
        """
        repr function for like/dislike
        """
        return {
                "like_count": value.likes().count(),
                "dislike_count": value.dislikes().count(),
                "sum_rating": value.sum_rating()
            }

class LikeDislikeSerializer(serializers.Serializer):
    """
    serializer class for the Like Dislike model
    """
    class Meta:
        model = LikeDislike
        pass
    
