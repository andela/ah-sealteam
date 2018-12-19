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
    article_slug = serializers.ReadOnlyField(source='article.slug')
    article_description = serializers.ReadOnlyField(source='article.description')
    article_author = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = BookmarkArticle
        fields = ('__all__')
        validators = [
            UniqueTogetherValidator(
                queryset=BookmarkArticle.objects.all(),
                fields=('article', 'user'),
                message='Sorry, you already bookmarked this article'
                )]
