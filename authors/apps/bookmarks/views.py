"""
Imports

"""
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView
)
from authors.apps.articles.models import Article
from authors.apps.articles.serializers import ArticleSerializer
from .models import BookmarkArticle
from .serializers import (
    BookmarkSerializer
)


class BookmarkPagination(PageNumberPagination):
    """
    Article pagination support
    """
    page_size = 10
    page_size_query_param = 'page_size'


class BookmarkAPIView(CreateAPIView):
    """
    Views for the bookmark functionality
    """
    serializer_class = BookmarkSerializer
    permission_classes = (IsAuthenticated,)


    def post(self, request, slug=None, pk=None):
        """
        Create a bookmark method
        """
        article = Article.objects.get(slug=slug)
        bookmark = {}
        bookmark['user'] = self.request.user.id
        bookmark['article'] = article.pk
        serializer = self.serializer_class(data=bookmark)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        article_serializer = ArticleSerializer(
            instance=article, context={'request': request})
        data = {"article": article_serializer.data}
        data["message"] = "bookmarked"

        return Response({
            "message": data.get('message'),
            "count": Article.objects.filter(slug=slug).count()
            }, status=status.HTTP_201_CREATED)

    def check_article(self, slug):
        """
        Check if article with the pass in slug exists
        if not
        :return 404
        """
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound(detail={'message': 'Article not found'})
        return article

    def check_bookmark(self, user, article):
        """
        check if the article has been bookmarked already
        if so return it else
        :return 404
        """
        try:
            bookmark = BookmarkArticle.objects.get(user=user, article=article.id)
        except BookmarkArticle.DoesNotExist:
            raise NotFound(detail={'message': 'This article has not been bookmarked'})
            
        return bookmark

    def delete(self, request, slug=None):
        """
        method for deleting an article a user has bookmarked
        """
        user = self.request.user.id
        article = self.check_article(slug)
        bookmark = self.check_bookmark(user, article)

        if bookmark:
            bookmark.delete()
        article_serializer = ArticleSerializer(
            instance=article, context={'request': request}
            )
        data = article_serializer.data
        data['message'] = 'Successfully removed from bookmark'
        return Response(
            {'message': data.get('message')}
            )

class BookmarkRetrieveAPIView(RetrieveAPIView):
    """
    Views to retrieve all bookmarks by the current user
    """
    serializer_class = BookmarkSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = BookmarkPagination

    def get_queryset(self):
        user = self.request.user
        return user.bookmarkarticle_set.all().order_by('-created_at')

    def get(self, request, slug=None):
        """
        get articles that the current logged in user has ever bookmarked
        """
        serializer = self.serializer_class(self.get_queryset(), many=True)
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response({'articles':serializer.data}, status=status.HTTP_200_OK)
