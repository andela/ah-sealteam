"""

Imports

"""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

from authors.apps.articles.utils import ChoicesField
from .models import Article, TaggedItem, ArticleRating, Photo, LikeDislike, Comment
from authors.apps.profiles.serializers import ProfileSerializer
from authors.apps.profiles.models import Profile

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

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    """This class creates the comments serializers"""

    author = serializers.SerializerMethodField()
    article = serializers.ReadOnlyField(source='article.title')
    thread = RecursiveSerializer(many=True, read_only=True)


    class Meta:
        model = Comment

        fields = (
            'id',
            'createdAt',
            'updatedAt',
            'body',
            'article',
            'author',
            'thread'
        )


    def get_author(self, obj):
        try:
            author = obj.author
            profile = Profile.objects.get(user_id=author.id)
            serializer = ProfileSerializer(profile)
            return serializer.data
        except Exception as e:
            print(e)
            return {}

    def create(self, validated_data):
        """
        Create and return a new comment instance, given the validated_data
        """
        parent = self.context.get('parent', None)
        instance = Comment.objects.create(parent=parent, **validated_data)
        return instance

    def update(self, instance, validated_data, **kwargs):
        """
        Update and return a comment instance, given the validated_data
        """
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        return instance


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
            'read_time',
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

class RatingSerializer(serializers.ModelSerializer):
    article = serializers.ReadOnlyField(source='article.id')
    user = serializers.ReadOnlyField(source="user.username")
    rate = ChoicesField(choices=ArticleRating.FIVE_REVIEWS)
    comment = serializers.CharField(required=False)

    class Meta:
        model = ArticleRating
        fields = (
            'id',
            'article',
            'user',
            'rate',
            'comment'
        )

    def create(self, validated_data):
        user_rates = ArticleRating.objects.filter(user=validated_data["user"],
                                                  article=validated_data["article"])
        if user_rates.exists():
            raise ValidationError("Not allowed to rate twice. "
                                  "Consider updating your rating")
        instance = ArticleRating.objects.create(**validated_data)
        return instance

class LikeDislikeSerializer(serializers.Serializer):
    """
    serializer class for the Like Dislike model
    """
    class Meta:
        model = LikeDislike
        pass
    
