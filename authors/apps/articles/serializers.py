"""

Imports

"""
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.Serializer):
    """
    This class creates the article serializers
    """
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Article

        fields = (
            'title',
            'description',
            'body'
        )

    def create(self, validated_data):
        """
        Create and return a new Article instance, given the validated_data
        """
        instance = Article.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing Article instance, give the validated_data
        """
        pass
