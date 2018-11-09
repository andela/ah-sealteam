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

    def get(self, request, username, format=None):
        """
            Check if the user associated with the username passed exists
            If true get friend objects associated with the user
            Get & return the followers from the respective object relationships i.e 'user_from'
        """
        user = get_object_or_404(get_user_model(), username=username)

        friend_objects = Friend.objects.select_related(
            'user_from', 'user_to').filter(user_to=user.id).all()
        followers = {u.user_from for u in friend_objects}
        followers = CustomUserSerializer(followers, many=True)

        if followers:
            return Response({"followers": followers.data}, status=status.HTTP_200_OK)
        return Response(followers.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowingAPIView(generics.ListAPIView):
    """View for getting users a user is following"""

    def get(self, request, username, format=None):
        """
            Check if the user associated with the username passed exists
            If true get friend objects associated with the user
            Get & return the 'followed users' from the respective object relationships i.e 'user_to'
        """
        user = get_object_or_404(get_user_model(), username=username)

        friend_objects = Friend.objects.select_related(
            'user_from', 'user_to').filter(user_from=user.id).all()
        users_followed = {u.user_to for u in friend_objects}
        users_followed = CustomUserSerializer(users_followed, many=True)
        if users_followed:
            return Response({"following": users_followed.data}, status=status.HTTP_200_OK)
        return Response(users_followed.errors, status=status.HTTP_400_BAD_REQUEST)
