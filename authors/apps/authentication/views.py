import re

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView, RetrieveUpdateAPIView
from django.views.generic import TemplateView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import User
from django.core.mail import send_mail
from rest_framework.generics import CreateAPIView
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from rest_auth.registration.views import (
    SocialLoginView, SocialConnectView, SocialAccountListView,
    SocialAccountDisconnectView
)
from rest_auth.social_serializers import (
    TwitterLoginSerializer, TwitterConnectSerializer
)
from rest_auth.serializers import LoginSerializer

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer, ResetPasswordSerializer,
    ForgotPasswordSerializer)

from django.contrib.auth.tokens import default_token_generator

class RegistrationAPIView(CreateAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data
        password = user.get("password")
        email = user.get("email")
        username = user.get("username")
        if not email:
            raise ValidationError({"email": "Please provide an email"})
        if not username:
            raise ValidationError({"username": "Please provide a an username"})
        if not password:
            raise ValidationError({"password": "Please provide a password"})

        if not re.match("^(?=.*\d).{8,20}$", password):
            raise ValidationError({"password": "Password must be between 8 - 20"
                                               " characters and at least 1 digit"})
        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetPasswordAPIView(UpdateAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ResetPasswordSerializer

    def update(self, request, *args, **kwargs):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        try:
            obj = User.objects.get(email=serializer.data["email"])
        except User.DoesNotExist:
            return Response({"Message": "User With The Email Address Was Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            new_password = serializer.data["password"]
            email = serializer.data["email"]

        user = User.objects.filter(email=serializer.data["email"]).first()
        is_valid_token = default_token_generator.check_token(user, serializer.data["token"])
        if is_valid_token is False:
            return Response({"Message": "Invalid email address or token. Please check your "
                                        "email or generate another reset password email"},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            obj.set_password(new_password)
            obj.save()
            send_mail(
                'SEAL TEAM',
                f'Greetings, \n Your password has been changed successfully. Your new password is {new_password}. \
                \n Keep it safe :-). \n Hope you have a lovely experience using our website.\
                \n \n Have Fun!!! \n Seal Team', 'simplysealteam@gmail.com', [email], fail_silently=False)
            return Response({'Success.': "Password Successfuly Reset"},
                            status=status.HTTP_200_OK)


class ForgotPasswordAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        user = request.data

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class GithubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter

class GithubConnect(SocialConnectView):
    adapter_class = GitHubOAuth2Adapter

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
 
class GoogleConnect(SocialConnectView):
    adapter_class = GoogleOAuth2Adapter

class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter

class TwitterLogin(SocialLoginView):
    adapter_class = TwitterOAuthAdapter
    serializer_class = TwitterLoginSerializer

class TwitterConnect(SocialConnectView):
    adapter_class = TwitterOAuthAdapter
    serializer_class = TwitterConnectSerializer
