from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import permissions
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.contrib.auth import get_user_model

from django.core.exceptions import ObjectDoesNotExist
from authors.apps.core.paginator import CustomPaginator

from .serializers import ProfileSerializer
from .models import Profile


class ProfileApiView(generics.ListAPIView):
    """
        View for fetching all the available profiles
    """
    permission_classes = (IsAuthenticated,)

    serializer_class = ProfileSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        return Profile.objects.exclude(user=self.request.user)

    def get(self, format=None):
        """
            Get  and return all the profiles
        """
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)


class ProfileRetrieve(generics.RetrieveAPIView):
    """
        View for fetching a single profile belonging to currently logged in user
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        """
            Get the user object using the passed in user
            Check if a profile belonging to the user exists
            if exists return it, else return not found
        """
        user = get_user_model().objects.get(id=request.user.id)
        profile = Profile.objects.get(user=user)

        serializer = self.serializer_class(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileRetrieveUpdate(generics.UpdateAPIView):
    """
        View for Updating the user's profile
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def put(self, request, username, format=None):
        """
            get the user object from the passed in username
            get the profile belonging to the passed in username
            pass the request data through the serializer
            check if valid and save
        """
        # Custom error handling
        try:
            user = get_user_model().objects.get(username=username)
        except ObjectDoesNotExist:
            raise Http404()

        profile = Profile.objects.get(user=user)
        # Custom permission handling
        if not profile.user.pk == request.user.id:
            return Response({"detail": "You are not allowed to update this user"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(
            profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, username, format=None):
        """
            get the user object from the passed in username
            get the profile belonging to the passed in username
            return the profile
        """
        try:
            user = get_user_model().objects.get(username=username)
        except ObjectDoesNotExist:
            raise Http404('The user cannot be found')
        profile = Profile.objects.get(user=user)
        serializer = self.serializer_class(profile)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
