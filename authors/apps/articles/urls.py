"""
 All Imports request on the file
"""

from django.urls import path
from .views import ArticleAPIView, ArticleRetrieveAPIView, RateAPIView, RateRetrieveAPIView

app_name = 'articles'

urlpatterns = [
    path('', ArticleAPIView.as_view(), name='create_article'),
    path('<slug:slug>', ArticleRetrieveAPIView.as_view(), name="retrieve_article"),
    path('<slug:slug>/rate', RateAPIView.as_view(), name="create_get_rating"),
    path('rate/detail/<int:rate_id>', RateRetrieveAPIView.as_view(), name="get_update_delete_rating")
]
