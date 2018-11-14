from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    reported_article = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = (
            'id', 'user', 'article', 'sender', 'reported_article', 'reason', 'created_at', 'updated_at'
        )

        extra_kwargs = {
            'reason': {'required': True},
            'user': {'write_only': True},
            'article': {'write_only': True}
        }

    def get_sender(self, obj):
        return {
            "username": obj.user.username,
            "email": obj.user.email,
        }

    def get_reported_article(self, obj):
        return {
            "slug": obj.article.slug,
            "title": obj.article.title,
            "description": obj.article.description
        }
