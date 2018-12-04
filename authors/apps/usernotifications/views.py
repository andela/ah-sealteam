"""
module for notification views
"""

# 3rd part imports
import jwt
from notifications.models import Notification
from rest_framework.generics import ( ListAPIView,
                                      DestroyAPIView,
                                      UpdateAPIView,
                                      ListCreateAPIView )
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import Http404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.tokens import default_token_generator

# local imports
from .serializers import NotificationSerializer, UnsubscribeSerializer
from .renderers import BaseJSONRenderer
from authors.apps.authentication.models import User


class NotificationAPIView(ListAPIView, DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer
    renderer_classes = (BaseJSONRenderer,)

    def get(self, request, *args, **kwargs):
        notifications = self.notifications(request)
        serializer = self.serializer_class(notifications, many=True, context={'request': request})
        # import pdb;pdb.set_trace()
        return Response({"count": notifications.count(), "notifications": serializer.data})

    def destroy(self, request, *args, **kwargs):
        notifications = self.notifications(request)
        count = notifications.count()
        notifications.mark_all_as_deleted()

        return Response({"message": "{} notifications deleted".format(count)})

    def notifications(self, request):
        pass


class AllNotificationsAPIView(NotificationAPIView):
    """
    List all the notifications for this user
    """

    def notifications(self, request):
        request.user.notifications.mark_as_sent()
        return request.user.notifications.active()


class UnreadNotificationsAPIView(NotificationAPIView):
    """
    List all unread notifications for this user
    """

    def notifications(self, request):
        request.user.notifications.mark_as_sent()
        return request.user.notifications.unread()


class ReadNotificationsAPIView(NotificationAPIView):
    """
    List all the Read  notifications for this user
    """
    
    def notifications(self, request):
        return request.user.notifications.read()

class ReadNotificationView(UpdateAPIView):
    """
    Mark a notification as read for this user
    """
    serializer_class = NotificationSerializer
    def update(self, request, *args, **kwargs):
        """
        handle put request to mark a notification as read
        """
        pk = kwargs['pk']
        notification = get_object_or_404(Notification, pk=pk)
        notification.mark_as_read()
        return Response({"message": "Notification has been read"})

class UnsentNotificationsAPIView(NotificationAPIView):
    """
    List all the unsent notifications
    """

    def notifications(self, request):
        return request.user.notifications.unsent()


class SentNotificationsAPIView(NotificationAPIView):
    """
    List all the sent notifications for this user
    """

    def notifications(self, request):
        return request.user.notifications.active().sent()

class UnSubscribeAPIView(ListAPIView, UpdateAPIView):
    """
    Allow users to unsubscribe from notifications
    """
    permission_classes = [AllowAny]
    renderer_classes = (BaseJSONRenderer,)
    serializer_class = UnsubscribeSerializer
    queryset = None
 
    def get(self, request, token):
        """
        unsubscribe from email notifications
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            user = get_object_or_404(User, id=payload['id'])
        except(TypeError, ValueError, OverflowError, Exception):
            raise Http404
        user.email_notification_subscription = False
        user.save()
        resp = {
            "message":"you have successfully changed notification status",
            "email":user.email_notification_subscription,
            "app":user.app_notification_subscription
        }
        return Response(resp, status=status.HTTP_200_OK)
    

    def put(self, request):
        """
        unsubscribe from app notifications
        """
        self.permission_classes.append(IsAuthenticated)
        user = get_object_or_404(User, email=request.user.email)
        user.app_notification_subscription = False
        resp = {
            "message":"you have successfully changed notification status",
            "email":user.email_notification_subscription,
            "app":user.app_notification_subscription
        }
        return Response(resp, status=status.HTTP_200_OK)


class SubscribeAPIView(ListCreateAPIView, UpdateAPIView):
    """
    Allow users to subscribe / unsubscribe to notifications
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = (BaseJSONRenderer,)

    def post(self, request):
        """
        subscribe to all notifications
        """
        user = get_object_or_404(User, email=request.user.email)
        user.email_notification_subscription = True
        user.app_notification_subscription = True
        resp = {
            "message":"you have successfully changed notification status",
            "email":user.email_notification_subscription,
            "app":user.app_notification_subscription
        }
        return Response(resp, status=status.HTTP_200_OK)
