""" This are the views for articles"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from authors.apps.articles.permissions import IsAuthorOrReadOnly

from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleSerializer


class ArticlePagination(PageNumberPagination):
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
            # removing body to improve on transfer performance
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
        return Response({"message": {"Article was deleted successful"}}, status.HTTP_200_OK)
