from rest_framework import serializers
from .models import Profile
from django.contrib.auth import get_user_model
from django.core.serializers import serialize
import json


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'user',
            'username',
            'bio',
            'image',
            'following',
            'followers',
        )

        extra_kwargs = {
            'user': {'read_only': True}
        }

    def get_username(self, obj):
        return obj.user.username

    def get_followers(self, obj):
        return len(json.loads(json.dumps([u.username for u in obj.user.followers.all()])))

    def get_following(self, obj):
        return len(json.loads(json.dumps([u.username for u in obj.user.following.all()])))
