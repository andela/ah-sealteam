"""
Imports
"""
from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers
from rest_framework.response import Response
from authors.apps.articles.models import Article
from .serializers import HighlightSerializer
from .models import Highlight


class HighlightAPIView(CreateAPIView):
    """
    highlight views to to send data to the models
    for processing and saving in the databaase
    """
    serializer_class = HighlightSerializer
    permission_classes = (IsAuthenticated,)

    def get_article(self, slug=None):
        """
        Get an article by its slug
        """
        try:
            article = Article.objects.get(slug=slug)
            return article
        except Article.DoesNotExist:
            raise serializers.ValidationError(
                "Article with the provided slug does not exit")

    def get_queryset(self, article):
        highlights = Highlight.objects.filter(article=article.id)
        return highlights.all()

    def check_if_exists(self, highlighted, article):
        """
        Checks if the highlighted text exists in the article body
        """
        content = article.body
        if highlighted in content:
            return highlighted

    def post(self, request, slug=None):
        """
        Create a new highlight and a new comment
        And updates the existing highlight
        """
        user = self.request.user
        data = request.data
        article = self.get_article(slug)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        highlight = self.check_if_exists(data.get('highlighted'), article)
        # check the highlight in the databaset
        try:
            exists = Highlight.objects.get(user=user, article=article,
                                           highlighted=data.get('highlighted'))
            if exists:
                # if exists, update it and save the insatnce
                exists.highlight = data.get('highlighted')
                exists.comment = data.get('comment')
                exists.save()
                return Response({"message": "Updated the highlighted text"})
        except Exception:
            pass
        if highlight:
            # Save the highlight in the database
            serializer.save(user=user, article=article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': {'message': 'The highlighted text does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)

    def get(self, request, slug=None):
        """
        Get the highlights for this specific article
        """
        article = self.get_article(slug=slug)
        serializer = self.serializer_class(self.get_queryset(article), many=True)
        if not serializer.data:
            return Response({'message': 'This article has no highlights'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({'highlights': serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, slug=None):
        """
        remove the highlight from the article
        """
        user = request.user.id
        article = self.get_article(slug=slug)
        try:
            highlight = Highlight.objects.get(user=user, article=article.id)
            if highlight:
                highlight.delete()
                return Response({"message": "Highlight removed successfully!"},
                                status=status.HTTP_200_OK) 
        except Highlight.DoesNotExist:
            raise NotFound(detail={'message': 'This article has no such highlight'})
