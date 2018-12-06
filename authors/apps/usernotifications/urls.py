"""
module for url configs

"""
import notifications.urls
from django.urls import path, include

from .views import (
    AllNotificationsAPIView,
    UnreadNotificationsAPIView,
    ReadNotificationsAPIView,
    UnsentNotificationsAPIView, 
    SentNotificationsAPIView,
    SubscribeAPIView,
    UnSubscribeAPIView,
    ReadNotificationView
    )

app_name = "notifications"

urlpatterns = [
    path('all/', AllNotificationsAPIView.as_view(), name="all-notifications"),
    path('unread/', UnreadNotificationsAPIView.as_view(), name="unread-notifications"),
    path('read/', ReadNotificationsAPIView.as_view(), name="read-notifications"),
    path('read/<int:pk>/', ReadNotificationView.as_view(), name="read-notification"),
    path('unsent/', UnsentNotificationsAPIView.as_view(), name="unsent-notifications"),
    path('sent/', SentNotificationsAPIView.as_view(), name="sent-notifications"),
    path('unsubscribe/<token>', UnSubscribeAPIView.as_view(), name="email-unsubscribe"), # get
    path('unsubscribe/', UnSubscribeAPIView.as_view(), name="app-unsubscribe"), # put
    path('subscribe/', SubscribeAPIView.as_view(), name="subscribe") # post
]
