"""
 All Imports request on the file
"""

from django.urls import path
from .views import ArticleAPIView, ArticleRetrieveAPIView

app_name = 'articles'

urlpatterns = [
    path('', ArticleAPIView.as_view(), name='create_article'),
    path('<int:pk>', ArticleRetrieveAPIView.as_view(), name="retrieve_article"),
]
