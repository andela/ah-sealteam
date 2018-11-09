from rest_framework import serializers
from django.contrib.auth import get_user_model


class CustomUserSerializer(serializers.ModelSerializer):
    """Custom user serializer for getting usernames"""
    class Meta:
        model = get_user_model()
        fields = ('username',)
