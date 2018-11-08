"""
Imports
"""
from django.urls import path
from .views import BookmarkAPIView, BookmarkRetrieveAPIView

app_name = 'bookmarks'

urlpatterns = [
    path('<slug:slug>/bookmark/', BookmarkAPIView.as_view(), name='bookmarks'),
    path('bookmarks/', BookmarkRetrieveAPIView.as_view(), name='all_bookmarks'),
]
