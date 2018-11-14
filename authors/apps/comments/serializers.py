"""
Serializers for comments app
"""
from rest_framework import serializers

from .models import Comment
from authors.apps.likedislike.models import LikeDislike 
from authors.apps.likedislike.serializers import VoteObjectRelatedSerializer
from authors.apps.profiles.models import Profile
from authors.apps.profiles.serializers import ProfileSerializer

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    """This class creates the comments serializers"""

    author = serializers.SerializerMethodField()
    article = serializers.ReadOnlyField(source='article.title')
    thread = RecursiveSerializer(many=True, read_only=True)
    votes = VoteObjectRelatedSerializer(read_only=True)

    class Meta:
        model = Comment

        fields = (
            'id',
            'createdAt',
            'updatedAt',
            'body',
            'article',
            'author',
            'votes',
            'thread'
        )


    def get_author(self, obj):
        author = obj.author
        profile = Profile.objects.get(user_id=author.id)
        serializer = ProfileSerializer(profile)
        return serializer.data

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


