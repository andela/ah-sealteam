"""
Adapting a social auth account to a user
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import perform_login
from .models import User

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    This class provides the option to add additional
    functionality to the allauth login pipeline
    """

    def pre_social_login(self, request, sociallogin):
        """
        this signal is sent after user is authenticated by
        social media provider but before the login is completed
        """
        user = sociallogin.user

        if user.id:
            return
        if not user.email:
            return
        try:
            emails = [email.email for email in sociallogin.email_addresses]
            user = User.objects.get(email__in=emails)
            # if user exists, connect the account to the existing account then login
            sociallogin.state['process'] = 'connect'
            sociallogin.connect(request, user)
            perform_login(request, user, 'none')
        except User.DoesNotExist:
            pass
