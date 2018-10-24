from rest_framework.test import APIClient
from django.test import TestCase
from .apps.authentication.models import User

class BaseTestCase(TestCase):
    """
    The base test case that all the test classes will use throughout
    the project
    """

    def setUp(self):
        self.client = APIClient()
        self.new_user = {
            'username': 'asheuh',
            'email': 'asheuh@gmail.com',
            'password': 'Mermaid@914'
        }
        User.objects.create_superuser(self.new_user.get('username'),
                                 self.new_user.get('email'), self.new_user.get('password'))

