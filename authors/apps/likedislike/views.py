"""
Views module for like dislike
"""

from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from authors.apps.articles.models import Article
from authors.apps.comments.models import Comment
from .serializers import LikeDislikeSerializer
from .models import LikeDislike


class LikeDislikeView(CreateAPIView):
    """
    this class defines the endpoint for like and dislike
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = LikeDislikeSerializer
    model = None    # Data Model - Article or Comment
    vote_type = None # Vote type Like/Dislike
 
    def post(self, request, slug=None, id=None):
        """
        This view enables a user to like or dislike an article
        """
        if self.model.__name__ is 'Article':
            obj = get_object_or_404(Article, slug=slug)
        else: # model is comment
            obj = get_object_or_404(Comment, id=id)
        # GenericForeignKey does not support get_or_create
        # the code is therefore wrapped in a try.. except 
        try:
            like_dislike = LikeDislike.objects.get(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=request.user )
            # check if the user has liked or disliked the article or comment already
            if like_dislike.vote is not self.vote_type:
                like_dislike.vote = self.vote_type
                like_dislike.save(update_fields=['vote'])
                result = True
            else:
                # delete the existing record if the user is submitting a similar vote
                like_dislike.delete()
                result = False
        except LikeDislike.DoesNotExist:
            # user has never voted for the article, create new record.
            obj.votes.create(user=request.user, vote=self.vote_type)
            result = True
 
        return Response({
                    "result": result,
                    "like_count": obj.votes.likes().count(),
                    "dislike_count": obj.votes.dislikes().count(),
                    "sum_rating": obj.votes.sum_rating()
                },
                content_type="application/json",
                status=status.HTTP_201_CREATED
            )
