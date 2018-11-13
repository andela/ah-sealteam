"""
activity stream configs
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    name = 'authentication'

    # def ready(self):
    #     from actstream import registry
    #     registry.register(self.get_model('User'))
