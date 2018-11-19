from rest_framework import serializers
from .models import Profile
from django.contrib.auth import get_user_model
from django.core.serializers import serialize
from authors.apps.authentication.serializers import UserSerializer
import json


class ProfileSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = (
            'user',
            'bio',
            'image',
            'following',
            'followers',
        )

        extra_kwargs = {
            'user': {'read_only': True}
        }

    def get_followers(self, obj):
        return len(json.loads(json.dumps([u.username for u in obj.user.followers.all()])))

    def get_following(self, obj):
        return len(json.loads(json.dumps([u.username for u in obj.user.following.all()])))
