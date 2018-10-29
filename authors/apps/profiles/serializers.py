from rest_framework import serializers
from .models import Profile
from django.contrib.auth import get_user_model
from authors.apps.authentication.serializers import UserSerializer


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'user',
            'username',
            'bio',
            'image'
        )

        extra_kwargs = {
            'user': {'read_only': True}
        }

    def get_username(self, obj):
        return obj.user.username
