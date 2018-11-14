"""
Imports

"""
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import BookmarkArticle

class BookmarkSerializer(serializers.ModelSerializer):
    """
    Bookmark serialization
    """
    article_name = serializers.ReadOnlyField(source='article.title')

    class Meta:
        model = BookmarkArticle
        fields = ('__all__')
        validators = [
            UniqueTogetherValidator(
                queryset=BookmarkArticle.objects.all(),
                fields=('article', 'user'),
                message='Sorry, you already bookmarked this article'
                )]
