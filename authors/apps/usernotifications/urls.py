"""
url patterns for user notifications
"""

from django.urls import path, include
import notifications.urls

# app_name="user_notifications"

urlpatterns = [
    path('notifications/', include(notifications.urls, namespace="notifications"))
]