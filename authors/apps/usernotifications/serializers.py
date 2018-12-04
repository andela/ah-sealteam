"""
serializer module for the user notifications app
"""
from rest_framework import serializers
from notifications.models import Notification

# local imports
from authors.apps.articles.models import Article
from authors.apps.comments.models import Comment
from authors.apps.authentication.models import User
from authors.apps.comments.serializers import CommentSerializer
from authors.apps.articles.serializers import ArticleSerializer
from authors.apps.profiles.models import Profile
from authors.apps.profiles.serializers import ProfileSerializer



class UnsubscribeSerializer(serializers.Serializer):
    """
    serializer class for email unsubscription
    """

    class Meta:
        fields = ('message', 'email', 'app')

class ActorTargetField(serializers.RelatedField):
    """
    To represent an actor / target
    """

    def to_representation(self, value):
        actor_type = "None"
        data = []
        if isinstance(value, Article):
            actor_type = "article"
            data = value.slug
        elif isinstance(value, Comment):
            actor_type = "comment"
            data = value.body
        elif isinstance(value, User):
            actor_type = "user"
            data = value.username
        return {
            "type": actor_type,
            "data": data
        }

    def to_internal_value(self, data):
        return Notification(data)

class NotificationSerializer(serializers.ModelSerializer):
    """
    serializer class for notification objects
    """
    actor = ActorTargetField(read_only=True)
    target = ActorTargetField(read_only=True)
    class Meta:
        model = Notification

        fields = ('id', 'actor', 'verb', 'target', 'level', 'unread', 'timestamp', 'description', 'emailed')
