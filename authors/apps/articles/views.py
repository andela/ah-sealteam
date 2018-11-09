""" This are the views for articles"""
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from authors.apps.articles.permissions import IsAuthorOrReadOnly, \
    NotArticleOwner, IsRaterOrReadOnly
from .models import Article, LikeDislike, ArticleRating, Comment
from .renderers import ArticleJSONRenderer, CommentJSONRenderer
from .serializers import ArticleSerializer, CommentSerializer, \
    RatingSerializer, LikeDislikeSerializer


class ArticlePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20


class ArticleAPIView(generics.ListAPIView):
    """
    A user can post an artcle once they have an account in the application
    params: ['title', 'description', 'body']
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer
    pagination_class = ArticlePagination
    renderer_classes = (ArticleJSONRenderer,)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Article.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(author__username__iexact=username)
        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            queryset = queryset.filter(tags__tag_name__iexact=tag)
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(slug__icontains=search) |
                Q(description__icontains=search) |
                Q(body__contains=search)
            )

        return queryset

    def post(self, request):
        """
        Create a new article in the application
        """
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Get all the articles ever posted in the application
        """
        self.queryset = self.get_queryset()
        serializer = self.serializer_class(self.queryset, many=True)
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            # removing body and comments to improve on transfer performance
            for article in serializer.data:
                article.pop("body")
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    """
    Views to retrieve a single article in the application
    """
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    serializer_class = ArticleSerializer

    def get_object(self):
        obj = get_object_or_404(self.queryset, slug=self.kwargs["slug"])
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, slug=None):
        """
        Retrieve a single article from the application
        """
        article = get_object_or_404(self.queryset, slug=slug)
        serializer = self.serializer_class(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, slug=None, **kwargs):
        """This function will update article"""
        article_update = self.get_object()
        serializer = self.serializer_class(
            article_update, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug=None, **kwargs):
        """This function will delete the article"""
        article_delete = self.get_object()
        article_delete.delete()
        return Response({"message": {"Article was deleted successful"}},
                        status.HTTP_200_OK)


class RateAPIView(CreateAPIView):
    """
    A user can post an artcle once they have an account in the application
    params: ['title', 'description', 'body']
    """
    permission_classes = (IsAuthenticatedOrReadOnly, NotArticleOwner)
    serializer_class = RatingSerializer
    pagination_class = ArticlePagination

    def get_queryset(self):
        """Overriding queryset to get only the article ratings"""
        return ArticleRating.objects.filter(article=self.get_object())

    def get_object(self):
        """Overriding object to get article_id"""
        obj = get_object_or_404(Article, slug=self.kwargs["slug"])
        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request, **kwargs):
        """
        Create a new article in the application
        """
        data = request.data
        serializer = self.serializer_class(data=data)
        article = self.get_object()
        if serializer.is_valid():
            serializer.save(user=self.request.user, article=article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_average_rating(self):
        """This function will calculate average"""
        queryset = ArticleRating.objects.filter(article_id=self.get_object())
        return queryset.aggregate(Avg('rate')).get("rate__avg")

    def get(self, request, slug):
        """
        Get all the articles ever posted in the application
        """
        rate = self.request.query_params.get('rate', None)
        if rate is not None:
            return Response({"average": self.get_average_rating()})

        serializer = self.serializer_class(self.get_queryset(), many=True)
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RateRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    """
    Views to retrieve a single article in the application
    """
    queryset = ArticleRating.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsRaterOrReadOnly)
    serializer_class = RatingSerializer

    def get_object(self):
        """Get ratings"""
        obj = get_object_or_404(self.queryset, pk=self.kwargs["rate_id"])
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, pk=None, **kwargs):
        """
        Retrieve a single rating
        """
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, **kwargs):
        """This function will update rating"""
        rate_update = self.get_object()
        serializer = self.serializer_class(
            rate_update, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, **kwargs):
        """This function will delete the article"""
        rate_delete = self.get_object()
        rate_delete.delete()
        return Response({"message": "Your rate was successfully deleted"},
                        status.HTTP_200_OK)


class LikeDislikeView(CreateAPIView):
    """
    this class defines the endpoint for like and dislike
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = LikeDislikeSerializer
    model = None  # Data Model - Articles or Comments
    vote_type = None  # Vote type Like/Dislike

    def post(self, request, slug):
        """
        This view enables a user to like or dislike an article
        """
        obj = self.model.objects.get(slug=slug)
        # GenericForeignKey does not support get_or_create
        # the code is therefore wrapped in a try.. except 
        try:
            like_dislike = LikeDislike.objects.get(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=request.user)
            # check if the user has liked or disliked the article
            # or comment already
            if like_dislike.vote is not self.vote_type:
                like_dislike.vote = self.vote_type
                like_dislike.save(update_fields=['vote'])
                result = True
            else:
                # delete the existing record if the user is submitting
                #  a similar vote
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


class ArticleCommentAPIView(CreateAPIView):
    """A user can comment on an article"""
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer

    def post(self, request, slug=None, **kwargs):
        """Comment on an article in the application
        :param **kwargs:
        """
        renderer_classes = (CommentJSONRenderer,)
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
            response = []
            response.append({'comments': comments})
        commentsCount = len(comments)
        if commentsCount == 0:
            return Response({"Message":
                                 "There are no comments for this article"},
                            status=status.HTTP_200_OK)
        elif commentsCount == 1:
            return Response(response, status=status.HTTP_200_OK)
        else:
            response.append({"commentsCount": commentsCount})
            return Response(response, status=status.HTTP_200_OK)


class ArticleCommentUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView,
                                        CreateAPIView):
    """Views to edit a comment in the application"""
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    serializer_class = CommentSerializer

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
        return Response(
            {"Message": "Comment with the specifid id was not found"})

    def update(self, request, slug=None, pk=None, **kwargs):
        """This function will update article"""
        comment = self.get_object()
        if comment == None:
            return Response({
                "message": "Comment with the specified id "
                           "for this article does Not Exist"},
                status=status.HTTP_404_NOT_FOUND)
        data = request.data
        serializer = self.serializer_class(comment, data=request.data,
                                           partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, slug=None, pk=None, **kwargs):
        """This function will delete the article"""
        comment = self.get_object()
        if comment == None:
            return Response({
                "message": "Comment with the specified id "
                           "for this article does Not Exist"},
                status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response({"message": {"Comment was deleted successfully"}},
                        status.HTTP_200_OK)
