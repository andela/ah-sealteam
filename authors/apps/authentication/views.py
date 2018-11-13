import re

import jwt
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
# from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from jwt import InvalidSignatureError, ExpiredSignatureError
from rest_auth.registration.views import (
    SocialLoginView, SocialConnectView
)
from rest_auth.social_serializers import (
    TwitterLoginSerializer, TwitterConnectSerializer
)
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.generics import UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authors import settings
from .models import User
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer, ResetPasswordSerializer,
    ForgotPasswordSerializer)

from django.contrib.auth.tokens import default_token_generator
from datetime import datetime
from django.template.loader import render_to_string, get_template
from django.shortcuts import render, get_object_or_404

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
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ResetPasswordSerializer

    def get(self, request, token):
        return render(request, 'reset_password_form.html', context={"token": token})

    def post(self, request, token):
        data = request.data
        serializer = self.serializer_class(
            data=data, context={"token": token})
        if serializer.is_valid():
            email = data['email']
            user = get_object_or_404(User, email=email)
            token = user.token()
            return Response(dict(message="Congratulations! You have successfully changed your password.", token=token))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            token = serializer.data['token']
            username = serializer.data['username']
            email = serializer.data['email']
            time = datetime.now()
            time = datetime.strftime(time, '%d-%B-%Y %H:%M')
            currentsite_domain = '127.0.0.1:8000'
            reset_link = 'http://' + currentsite_domain + \
                '/api/users/resetpassword/{}/'.format(token)
            subject, from_email, to = 'Authors Haven', 'simplysealteam@gmail.com', [
                email]

            html_content = render_to_string('forgot_password_email.html', context={
                                            "reset_link": reset_link, "username": username, "time": time})
            send_mail(subject, '', from_email, to, html_message=html_content)

            return Response(dict(message="A link has been successfully sent to your email." \
                                    " Check your spam folder incase you don't find it."))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(username=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None:
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            user.email_verified = True
            user.save()
        except Exception as e:
            return Response({"token": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('User not found')


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
