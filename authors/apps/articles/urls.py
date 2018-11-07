"""
 All Imports request on the file
"""

from django.urls import path
from .views import ArticleAPIView, ArticleRetrieveAPIView, LikeDislikeView, RateAPIView, RateRetrieveAPIView, ArticleCommentAPIView, ArticleCommentUpdateDeleteAPIView
from .models import Article, LikeDislike

app_name = 'articles'

urlpatterns = [
    path('', ArticleAPIView.as_view(), name='create_article'),
    path('<slug:slug>', ArticleRetrieveAPIView.as_view(), name="retrieve_article"),
    path('<slug:slug>/rate', RateAPIView.as_view(), name="create_get_rating"),
    path('rate/detail/<int:rate_id>', RateRetrieveAPIView.as_view(), name="get_update_delete_rating"),
    path('<slug:slug>/like/',
         LikeDislikeView.as_view(model=Article, vote_type=LikeDislike.LIKE),
         name='article_like'),
    path('<slug:slug>/dislike/',
         LikeDislikeView.as_view(model=Article, vote_type=LikeDislike.DISLIKE),
         name='article_dislike'),
    path('<slug:slug>/comment/', ArticleCommentAPIView.as_view(), name='comment_article'),
    path('<slug:slug>/comment/<int:id>/', ArticleCommentUpdateDeleteAPIView.as_view(), name='update_comment')
]
