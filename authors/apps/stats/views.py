from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from authors.apps.articles.models import Article
from authors.apps.articles.serializers import ArticlePagination
from authors.apps.stats.models import ReadingStatistics
from authors.apps.stats.serializers import ReadingStatisticsSerializer, \
    MyArticleStacsSerializer


class ReadingStatisticsView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReadingStatisticsSerializer
    pagination_class = ArticlePagination

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return ReadingStatistics.objects.filter(user=self.get_object())

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            # removing body and comments to improve on transfer performance
            for article in serializer.data:
                article["article"].pop("body")
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status.HTTP_200_OK)


class MyArticlesReadingStacsView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MyArticleStacsSerializer
    pagination_class = ArticlePagination

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return Article.objects.filter(author=self.get_object())

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            # removing body and comments to improve on transfer performance
            for article in serializer.data:
                article.pop("body")
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status.HTTP_200_OK)
