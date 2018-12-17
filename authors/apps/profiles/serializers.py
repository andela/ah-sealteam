from rest_framework import serializers
from .models import Profile
from authors.apps.articles.models import Article
from django.contrib.auth import get_user_model
from django.core.serializers import serialize
from authors.apps.authentication.serializers import UserSerializer
import json


class ProfileSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    articles = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'firstname',
            'lastname',
            'username',
            'bio',
            'image',
            'following',
            'followers',
            'articles'
        )

        extra_kwargs = {
            'user': {'read_only': True}
        }

    def get_followers(self, obj):
        return len(json.loads(json.dumps([u.username for u in obj.user.followers.all()])))

    def get_following(self, obj):
        return len(json.loads(json.dumps([u.username for u in obj.user.following.all()])))

    def get_articles(self, obj):
        return len(Article.objects.filter(author=obj.user))

    def get_username(self, obj):
        return obj.user.username

