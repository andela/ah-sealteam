"""

Imports

"""
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from .models import Article, TaggedItem, Photo

class ArticlePagination(PageNumberPagination):
    """
    Article pagination serialization
    """
    page_size = 10
    page_size_query_param = 'page_size'


class TaggedOjectRelatedField(serializers.RelatedField):
    """
    A custom field to use for the tagged_object generic relationship
    """

    def get_queryset(self):
        return TaggedItem.objects.all()

    def to_representation(self, value):
        """
        Serialize tagged objects to a single textual representation
        """
        if isinstance(value, TaggedItem):
            return value.tag_name
        raise Exception('Unexpected type of tagged object')

    def to_internal_value(self, data):
        return TaggedItem.objects.create(tag_name=data)


class ArticleSerializer(serializers.ModelSerializer):
    """
    This class creates the article serializers
    """
    author = serializers.ReadOnlyField(source='author.username')
    tags = TaggedOjectRelatedField(many=True)
    
    class Meta:
        model = Article

        fields = (
            'slug',
            'title',
            'description',
            'tags',
            'createdAt',
            'updatedAt',
            'favorited',
            'body',
            'author'
        )


    def create(self, validated_data):
        """
        Create and return a new Article instance, given the validated_data
        """
        tags = validated_data.pop('tags')
        instance = Article.objects.create(**validated_data)
        for tag in tags:
            new_tag = TaggedItem(tagged_object=instance, tag_name=tag.tag_name)
            new_tag.save()

        return instance

    def update(self, instance, validated_data, **kwargs):
        """
        Update and return an existing Article instance, give the validated_data
        """
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.favorited = validated_data.get('favorited', instance.favorited)
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        return instance


class ImageFileSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

class PhotoSerializer(serializers.Serializer):
    """
    This class performs the serialization of the images
    """
    class Meta:
        model = Photo
        fields = ('article',)
