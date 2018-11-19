"""
This module defines the views for the comments app
"""

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.contrib.contenttypes.models import ContentType

from .models import Comment
from .serializers import CommentSerializer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
from .renderers import CommentJSONRenderer
from authors.apps.articles.permissions import IsAuthorOrReadOnly
from authors.apps.articles.models import Article
from authors.apps.likedislike.models import LikeDislike

class CommentPagination(PageNumberPagination):
    """
    Article pagination support
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20


class ArticleCommentAPIView(CreateAPIView):
    """A user can comment on an article"""
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer
    renderer_classes = (CommentJSONRenderer,)
    pagination_class = CommentPagination
    

    def post(self, request, slug=None):
        """Comment on an article in the application"""
        article = get_object_or_404(Article, slug=self.kwargs["slug"]) 
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(author=self.request.user, article=article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, slug=None):
        """Get all the comments of an article"""
        article = get_object_or_404(Article, slug=self.kwargs["slug"])
        comment_set = Comment.objects.filter(article__id=article.id)
        comments = []
        for comment in comment_set:
            serializer = CommentSerializer(comment)
            comments.append(serializer.data)
        commentsCount = len(comments)
        if commentsCount == 0:
            return Response({"Message":"There are no comments for this article"}, status=status.HTTP_200_OK) 
        elif commentsCount == 1:
            return Response(comments, status=status.HTTP_200_OK) 
        else:
            comments.append({"commentsCount":commentsCount})
            page = self.paginate_queryset(comment_set)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)


class ArticleCommentUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView, CreateAPIView):
    """Views to edit a comment in the application"""
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer
    renderer_classes = (CommentJSONRenderer,)

    def get_object(self):
        article = get_object_or_404(Article, slug=self.kwargs["slug"])
        comment_set = Comment.objects.filter(article__id=article.id)
        if not comment_set:
            raise Http404
        for comment in comment_set:
            new_comment = get_object_or_404(Comment, pk=self.kwargs["id"])
            if comment.id == new_comment.id:
                self.check_object_permissions(self.request, comment)
                return comment

    def create(self, request, slug=None, pk=None, **kwargs):
        data = request.data
        context = {'request': request}
        comment = self.get_object()
        context['parent'] = comment = Comment.objects.get(pk=comment.id)
        if context['parent']:
            serializer = self.serializer_class(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


    def update(self, request, pk=None, **kwargs):
        """This function will update article"""
        self.permission_classes.append(IsAuthorOrReadOnly)
        comment = get_object_or_404(Comment, pk=self.kwargs["id"])
        self.check_object_permissions(self.request, comment)
        data = request.data
        serializer = self.serializer_class(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"comment" : serializer.data, "Status": "Edited" }, status=status.HTTP_201_CREATED)

    def delete(self, request, slug=None, pk=None, **kwargs):
        """This function will delete the article"""
        self.permission_classes.append(IsAuthorOrReadOnly)
        comment = get_object_or_404(Comment, pk=self.kwargs["id"])
        self.check_object_permissions(self.request, comment)
        serializer = self.serializer_class(comment)
        comment.delete()
        return Response("Successfully Deleted")

class ImmediateCommentHistoryAPIView(RetrieveAPIView):
    """View to retrieve a previous comment"""
    renderer_classes = (CommentJSONRenderer,)


    def get(self, request, slug=None, id=None):
        article = get_object_or_404(Article, slug=self.kwargs["slug"])
        comment_set = Comment.objects.filter(article__id=article.id)
        if comment_set.exists():
            for comment in comment_set:
                if comment.id == self.kwargs['id']:
                    newcomment = Comment.history.filter(id=self.kwargs['id'])
                    if not newcomment or newcomment.count() == 1:
                        return Response({'Message':'This comment has not been edited before'}, \
                                            status=status.HTTP_404_NOT_FOUND)
                    previous_comment = newcomment[1]
                    serializer = CommentSerializer(previous_comment)
                    response = []
                    response.append(serializer.data)
                    return Response(response, status=status.HTTP_200_OK)
                return Response({"Message":"The comment with the specified id does not belong to this article"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"Message":"This article has no comments"})

class AllCommentHistoryAPIView(RetrieveAPIView):
    """View to retrieve all previous comment"""
    serializer_class = CommentSerializer
    pagination_class = CommentPagination

    def get(self, request, slug=None, id=None):
        renderer_classes = (CommentJSONRenderer,)
        article = get_object_or_404(Article, slug=self.kwargs["slug"])
        comment_set = Comment.objects.filter(article__id=article.id)
        if comment_set.exists():
            for comment in comment_set:
                comments = []
                newcomments = Comment.history.filter(id=self.kwargs['id'])
                if not newcomments:
                    return Response({'Message':'This comment does not exist'}, status=status.HTTP_404_NOT_FOUND)
                for history_comment in newcomments:
                    if comment.id == history_comment.id:
                        page = self.paginate_queryset(newcomments)
                        if page is not None:
                            serializer = self.serializer_class(page, many=True)
                            return self.get_paginated_response(serializer.data)
                    return Response({"Message":"The comment with the specified id does not belong to this article"})
        return Response({"Message":"This article has no comments"})
