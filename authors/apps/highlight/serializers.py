"""
Imports
"""
from rest_framework import serializers
from .models import Highlight

class HighlightSerializer(serializers.ModelSerializer):
    """
    Serializing the data received from the models
    to display in dictionary format
    """
    highlighted = serializers.CharField(
        required=True,
        error_messages={"required": "Highlighted field is required"})

    class Meta:
        model = Highlight
        fields = ('user', 'article', 'comment', 'highlighted')

    def create(self, validated_data):
        instance = Highlight.objects.create(**validated_data)
        return instance
