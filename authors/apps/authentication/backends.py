import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User

"""Configure JWT Here"""


class JWTAuthentication(authentication.BaseAuthentication):
    """This class will override default Base authentication and do authentication with Token"""

    def authenticate(self, request):
        """This methods overrides the base method and does the authentication"""
        token = authentication.get_authorization_header(request).decode('utf-8')
        if not token:
            return None
        try:
            token = token.split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        except Exception as e:
            raise exceptions.AuthenticationFailed("Invalid token")
        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User does not exist")
        return user, token
