"""
Imports
"""

from django.urls import path
from .views import HighlightAPIView

app_name = 'highlight'

urlpatterns = [
    path('<slug:slug>/highlight/', HighlightAPIView.as_view(), name='highlight'),
    path('<slug:slug>/highlights/', HighlightAPIView.as_view(), name='highlights'),
]
