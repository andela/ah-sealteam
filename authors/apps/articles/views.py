"""

Imports

"""
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Article
from .serializers import ArticleSerializer

# Create your views here.

class ArticleAPIView(CreateAPIView):
    """
    A user can post an artcle once they have an account in the application
    params: ['title', 'description', 'body']
    """
    queryset = Article.objects
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer

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
        serializer = self.serializer_class(self.queryset.all(), many=True)
        return Response({'articles': serializer.data}, status=status.HTTP_200_OK)


class ArticleRetrieveAPIView(RetrieveAPIView):
    """
    Views to retrieve a single article in the application
    """
    queryset = Article.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = ArticleSerializer

    def retrieve(self, request, pk=None):
        """
        Retrieve a single articel fromthe application
        """
        article = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(article)
        return Response(serializer.data, status=status.HTTP_200_OK)
