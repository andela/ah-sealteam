"""
This module defines the url patterns for the comments app
"""
from django.urls import path, include
from .views import ArticleCommentAPIView, ArticleCommentUpdateDeleteAPIView
from .models import Comment
from authors.apps.likedislike.models import LikeDislike
from authors.apps.likedislike.views import LikeDislikeView

app_name = 'comments'

urlpatterns = [
    path('comments/', ArticleCommentAPIView.as_view(), name='comment_article'),
    path('comments/<int:id>/', ArticleCommentUpdateDeleteAPIView.as_view(), name='update_comment'),
    path('comments/<int:id>/like',
         LikeDislikeView.as_view(model=Comment,
         vote_type=LikeDislike.LIKE),
         name="comment_like"),
    path('comments/<int:id>/dislike', 
         LikeDislikeView.as_view(model=Comment,
         vote_type=LikeDislike.DISLIKE),
         name="comment_dislike")
]
