from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Favorite
from authors.apps.articles.models import Article
import json

class FavoriteObjectRelatedSerializer(serializers.RelatedField):
    """
    A custom field to use for the favorites generic relationship
    """
    def get_queryset(self):
        return Favorite.objects.all()

    def to_representation(self, value):
        """
        repr function for like/dislike
        """
        return {
                "count": value.favorites().count(),
            }

class FavoriteSerializer(serializers.ModelSerializer):
    """
    Favorite serializer class
    """
    article = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ('content_type', 'user', 'article', 'object_id')
        validators = [
            UniqueTogetherValidator(
                queryset = Favorite.objects.all(),
                fields=('object_id', 'user'),
                message="Article is already favorited"
            )
        ]
    
    def get_article(self, instance):
        from authors.apps.articles.serializers import ArticleSerializer
        _id = instance.object_id
        article = Article.objects.get(pk=_id)
        serializer = ArticleSerializer(article)
        return serializer.data