from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from authors.apps.articles.utils import ChoicesField
from .models import Article, TaggedItem, ArticleRating
from authors.apps.profiles.serializers import ProfileSerializer
from authors.apps.profiles.models import Profile
from authors.apps.likedislike.serializers import VoteObjectRelatedSerializer
from authors.apps.favorites.serializers import FavoriteObjectRelatedSerializer


class ArticlePagination(PageNumberPagination):
    """
    Article pagination serialization
    """
    page_size = 10
    page_size_query_param = 'page_size'


class TaggedItemSerializer(serializers.ModelSerializer):
    """
    This translates Tags models to serialized dates
    """

    class Meta:
        model = TaggedItem
        fields = ('tag_name',)

    def to_representation(self, instance):
        return instance.tag_name


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
        if isinstance(data, Article):
            raise Exception("Expected a type of object")
        return TaggedItem.objects.create(tag_name=data)



class ArticleSerializer(serializers.ModelSerializer):
    """
    This class creates the article serializers
    """
    author = serializers.SerializerMethodField()
    tags = TaggedOjectRelatedField(many=True)
    votes = VoteObjectRelatedSerializer(read_only=True)
    favorited = FavoriteObjectRelatedSerializer(read_only=True)
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
            'votes',
            'body',
            'read_time',
            'author',

        )


    def get_author(self, user):
        """
        Get the current user details
        """
        if isinstance(user, Article):
            author = user.author
            profile = Profile.objects.get(user_id=author.id)
            serializer = ProfileSerializer(profile)
            return serializer.data
        return {}

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
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        return instance


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

# class FavoriteSerializer(serializers.ModelSerializer):
#     """
#     Favorite serializer class
#     """
#     class Meta:
#         model = Favorite
#         fields = ('article', 'user')
#         validators = [
#             UniqueTogetherValidator(
#                 queryset = Favorite.objects.all(),
#                 fields=('article', 'user'),
#                 message="Article is already favorited"


#             )
#         ]
class ShareArticleSerializer(serializers.Serializer):
    share_with = serializers.CharField()
