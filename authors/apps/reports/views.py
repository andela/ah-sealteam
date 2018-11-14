from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from .permissions import OwnerPermission, SuperUserPermission

from .models import Report
from .serializers import ReportSerializer
from authors.apps.articles.models import Article
from authors.apps.core.paginator import CustomPaginator
from django.forms.models import model_to_dict


class ReportListAPIView(generics.ListAPIView):
    """View for listing all reports"""
    permission_classes = [SuperUserPermission]
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    pagination_class = CustomPaginator


class ReportListUserAPIView(generics.ListAPIView):
    """View for retrieving reports associated with the currently logged in user"""
    permission_classes = [OwnerPermission]
    serializer_class = ReportSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        """
            Return a list of all the reports
            for the currently authenticated user.
        """
        user = self.request.user
        return Report.objects.filter(user=user)

    def get(self, request, format=None):
        reports = self.paginate_queryset(self.get_queryset())
        serializer = self.serializer_class(reports, many=True)
        return self.get_paginated_response(serializer.data)


class ReportAPIView(generics.CreateAPIView):
    """View for reporting a specific article"""
    permission_classes = [IsAuthenticated]
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def get_object(self):
        """
            Check if the article associated with the slug passed exists
            If true return the article object
        """
        article = get_object_or_404(
            Article, slug=self.kwargs['slug'])
        return article

    def post(self, request, slug, format=None):
        """
            First check if the author of the article mathes the user reporting the article
            If true return an error message
            Get the data passed via the request and update the 
            resulting dictionary with the user and the article
            Serialize the data and save
        """
        article = self.get_object()
        user = request.user
        # Permissions
        if article.author == request.user:
            return Response({"message": "You cannot report your own article"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        data = request.data
        data.update({'article': article.pk, 'user': user.pk})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportActionsAPIView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting a report"""
    permission_classes = [OwnerPermission]
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    lookup_field = 'pk'

    def put(self, request, pk, format=None):
        """
            First check if the author of the report matches the user updating the report
            If not true return an error message
            Get the data passed via the request
            Serialize the data and update
        """

        report = get_object_or_404(Report, pk=self.kwargs['pk'])
        # Permissions
        if report.user != request.user:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)
        data = request.data
        serializer = self.serializer_class(report, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
