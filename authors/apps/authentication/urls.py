from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, ResetPasswordAPIView, ForgotPasswordAPIView,
    FacebookLogin, FacebookConnect, GithubLogin, GithubConnect,
    GoogleLogin, GoogleConnect, TwitterLogin, TwitterConnect, activate
)
from rest_auth.registration.views import (
    SocialAccountListView, SocialAccountDisconnectView
)

app_name = "authentication"

urlpatterns = [
    path('user', UserRetrieveUpdateAPIView.as_view(), name='update_user'),
    path('users', RegistrationAPIView.as_view(), name='register'),
    path('users/login', LoginAPIView.as_view(), name='login'),
    path('users/forgotpassword/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('users/resetpassword/', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='update_user'),
    path('users/', RegistrationAPIView.as_view(), name='register'),
    path('users/login/', LoginAPIView.as_view(), name='login'),
    path('users/forgotpassword/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('users/resetpassword/', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('social-login/facebook/', FacebookLogin.as_view(), name='fb_login'),
    path('social-login/facebook/connect/', FacebookConnect.as_view(), name='fb_connect'),
    path('social-login/twitter/', TwitterLogin.as_view(), name='tw_login'),
    path('social-login/twitter/connect/', TwitterConnect.as_view(), name='tw_connect'),
    path('social-login/google/', GoogleLogin.as_view(), name='gg_login'),
    path('social-login/google/connect/', GoogleConnect.as_view(), name='gg_connect'),
    path('social-login/github/', GithubLogin.as_view(), name='git_login'),
    path('social-login/github/connect/', GithubConnect.as_view(), name='git_connect'),
    path('socialaccounts/', SocialAccountListView.as_view(), name='social_account_list'),
    path('socialaccounts/<int:pk>/disconnect/', SocialAccountDisconnectView.as_view(),
         name='social_account_disconnect'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
]
