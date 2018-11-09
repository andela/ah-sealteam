from rest_framework import generics
from django.contrib.auth import get_user_model
from .models import Friend
from rest_framework.permissions import IsAuthenticated
from authors.apps.profiles.models import Profile
from .serializers import CustomUserSerializer
from authors.apps.profiles.serializers import ProfileSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from authors.apps.core.paginator import CustomPaginator


class FollowAPIView(generics.CreateAPIView):
    """View for following a user"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, username, format=None):
        """
            Check if the user associated with the username passed exists
            If true check for the user sending the request
            If the users are the same then return an error message
            Else use the intermediary Friend model to create the user relationship
            Finally return the profile of the followed user
        """
        try:
            followed = get_user_model().objects.get(username=username)
        except ObjectDoesNotExist:
            raise Http404()

        follower = get_user_model().objects.get(pk=request.user.id)

        if followed == follower:
            return Response({"message": "You cannot follow yourself"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        Friend.objects.get_or_create(
            user_from=follower,
            user_to=followed)

        profile = Profile.objects.get(user=followed)
        serializer = ProfileSerializer(profile)

        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)


class UnfollowAPIView(generics.DestroyAPIView):
    """View for unfollowing a user"""
    permission_classes = (IsAuthenticated,)

    def delete(self, request, username, format=None):
        """
            Check if the user associated with the username passed exists
            If true check for the user sending the request
            If the users are the same then return an error message
            Else use the intermediary Friend model to delete the user relationship
            Finally return the profile of the unfollowed user
        """
        try:
            followed = get_user_model().objects.get(username=username)
        except ObjectDoesNotExist:
            raise Http404()

        follower = get_user_model().objects.get(pk=request.user.id)

        if followed == follower:
            return Response({"message": "You cannot unfollow yourself"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        Friend.objects.filter(user_from=follower,
                              user_to=followed).delete()

        profile = Profile.objects.get(user=followed)
        serializer = ProfileSerializer(profile)

        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)


class FollowersAPIView(generics.ListAPIView):
    """View for getting users following a particular user"""
    pagination_class = CustomPaginator

    def get_queryset(self):
        """
            Check if the user associated with the username passed exists
            If true return friend objects associated with the user
        """
        user = get_object_or_404(
            get_user_model(), username=self.kwargs['username'])
        return Friend.objects.select_related(
            'user_from', 'user_to').filter(user_to=user.id).all()

    def get(self, request, username, format=None):
        """
            Paginate the returned friend objects from the queryset
            Get & return the followers from the respective object relationships i.e 'user_from'
        """
        friend_objects = self.paginate_queryset(self.get_queryset())
        if friend_objects is not None:
            followers = {u.user_from for u in friend_objects}
            serializer = CustomUserSerializer(followers, many=True)
            return self.get_paginated_response(serializer.data)


class FollowingAPIView(generics.ListAPIView):
    """View for getting users a user is following"""
    pagination_class = CustomPaginator

    def get_queryset(self):
        """
            Check if the user associated with the username passed exists
            If true return friend objects associated with the user
        """
        user = get_object_or_404(
            get_user_model(), username=self.kwargs['username'])
        return Friend.objects.select_related(
            'user_from', 'user_to').filter(user_from=user.id).all()

    def get(self, request, username, format=None):
        """
            Paginate the returned friend objects from the queryset
            Get & return the 'followed users' from the respective object relationships i.e 'user_to'
        """
        friend_objects = self.paginate_queryset(self.get_queryset())
        if friend_objects is not None:
            users_followed = {u.user_to for u in friend_objects}
            serializer = CustomUserSerializer(users_followed, many=True)
            return self.get_paginated_response(serializer.data)
