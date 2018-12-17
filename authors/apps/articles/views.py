""" This are the views for articles"""
import os
import datetime
# import sendgrid
# from decouple import config
from django.core.mail import send_mail

from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.exceptions import NotFound, PermissionDenied
from .renderers import ArticleJSONRenderer
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
# from django.core.mail import send_mail

from sendgrid.helpers.mail import(Content, Email, Mail)
from pyisemail import is_email
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.contrib.contenttypes.models import ContentType
from authors.apps.authentication.models import User

from authors.apps.articles.permissions import IsAuthorOrReadOnly, \
    NotArticleOwner, IsRaterOrReadOnly
from authors.apps.stats.models import ReadingStatistics
from .models import Article, ArticleRating, TaggedItem
from .renderers import ArticleJSONRenderer
from .serializers import ArticleSerializer, RatingSerializer, ShareArticleSerializer
from .serializers import (
    TaggedItemSerializer
)

from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

class ArticlePagination(PageNumberPagination):
    """
    Article pagination support
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20


class ArticleAPIView(CreateAPIView):
    """
    A user can post an artcle once they have an account in the application
    params: ['title', 'description', 'body']
    """
    queryset = Article.objects
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
        self.queryset = self.queryset.all()
        serializer = self.serializer_class(self.queryset, many=True)
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            # removing body and comments to improve on transfer performance
            for article in serializer.data:
                article.pop("body")
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TaggedItemRetrieveAPIView(RetrieveAPIView):
    """
    Making use of the viewsets to create the views for the tags
    """
    queryset = TaggedItem.objects
    serializer_class = TaggedItemSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    def get(self, request):
        """
        Getting all the tags in the application
        """
        serializer = self.serializer_class(self.queryset.all(), many=True)
        return Response({'tags':serializer.data}, status=status.HTTP_200_OK)

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
        if request.user and not isinstance(request.user, AnonymousUser):
            self.update_read(article)
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

    def update_read(self, article):
        """THis function will update no of reads on an article by user"""
        read_statistics = ReadingStatistics.objects.filter(
            user=self.request.user, article=article)
        if read_statistics:
            read_time = read_statistics[0].article.read_time
            read_time_int = int(read_time.split(' ')[0]) * 60
            no_sec = read_statistics[0].time_since_last_read().seconds
            if no_sec > int(read_time_int):
                read_statistics.update(no_read=read_statistics[0].no_read +
                                               1, read_last_at=
                datetime.datetime.now())
        else:
            ReadingStatistics.objects.create(user=self.request.user,
                                             article=article)

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

class ShareArticleAPIView(CreateAPIView):
    """
    Class for article share
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ShareArticleSerializer

    def post(self, request, slug):
        """
        Method for sharing article via email
        """
        sender = request.user.email
        sharer = request.user.username
        article_shared = request.data.get('article', {})
        serializer = self.serializer_class(data=article_shared)
        serializer.is_valid(raise_exception=True)
        host = os.getenv("DOMAIN")
        shared_article_link = host + \
        '/api/articles/{}'.format(slug)
        if not is_email(article_shared['share_with']):
            raise serializers.ValidationError({
                'email': 'Enter a valid email address.'
            })
        share_article(sharer, shared_article_link, sender, article_shared['share_with'])

        return Response({"message": "Article shared successfully"}, status.HTTP_200_OK)

def share_article(sharer, host, sender, reciever_email):
    """
    This formats how the message would appear on the mail box
    """
    message_subject = "{} from Seal Team, shared an article with you via Authors Haven".format(sharer)
    content =  """Hello, \n
        {} via Authors Haven has shared an article with you.
        Kindly click the link below to read the article.
        {}""".format(sharer, host)
        
    response = send_mail(message_subject, content, sender, [reciever_email])
    return response
