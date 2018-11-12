from django.urls import path

from . import views

urlpatterns = [
    path('follow', views.FollowAPIView.as_view(), name='follow'),
    path('unfollow', views.UnfollowAPIView.as_view(), name='unfollow'),
    path('followers', views.FollowersAPIView.as_view(), name='followers'),
    path('following', views.FollowingAPIView.as_view(), name='following')
]
