from django.shortcuts import render, get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from .models import Favorite
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from rest_framework.response import Response
from .serializers import FavoriteSerializer
from django.core import serializers
from authors.apps.articles.serializers import ArticleSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

class FavoritePagination(PageNumberPagination):
    """
    Favorite pagination 
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20


class FavoriteArticle(CreateAPIView):
    """
    View for user favorite an article
    """
    permission_classes = (IsAuthenticated,)
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    

    def post(self, request, slug):
        """
        This method favorites an article.
        """

        article = get_object_or_404(Article, slug=slug)
        fav_article = ContentType.objects.get_for_model(Article)   
        favorite_user = {
            "user":request.user.id,
            "content_type":fav_article.pk,
            "article_object":article,
            "object_id":article.id
        }
        serializer = self.serializer_class(data=favorite_user,
                                           context={"request":request})
        data = {
            "slug":article.slug
        }
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError:
            Favorite.objects.get(user=request.user, object_id=article.id).delete()

        article_s = ArticleSerializer(article)

        return Response(article_s.data, status=status.HTTP_200_OK)

class FavoriteArticleRetrieve(RetrieveAPIView):
    """
    View to retrieve all favorites for a logged in user
    """
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = FavoritePagination

    def get_queryset(self):
        """
        This method gets all favorites made
        """
        
        user = self.request.user
        return user.favorite_set.all().order_by('-created_at')

    def get(self, request):
        """
        This method Get all articles favorited for a logged in user
        """
        # pagination
        serializer = self.serializer_class(self.get_queryset(), many=True)
        page = self.paginate_queryset(self.get_queryset())

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response({'articles':serializer.data}, status=status.HTTP_200_OK)

