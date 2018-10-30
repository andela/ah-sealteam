from django.urls import reverse
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
        self.register_url = reverse('authentication:register')
        self.user_url = reverse('authentication:update_user')
        self.username = "mike"
        self.wrongmail = "dennis mail.com"
        self.email = "testemail@gmail.com"
        self.password = "testpasswor67d"
        self.login_url = reverse("authentication:login")
        self.reset_password_url = reverse("authentication:reset_password")
        self.forgot_password_url = reverse("authentication:forgot_password")
        # this user will be used to test login
        User.objects.create_user(username=self.username,
                                 email=self.email, password=self.password)
        data_for_get_test = {
                "email": self.email,
                "password": self.password
        }
        response = self.client.post(self.login_url, data_for_get_test, format='json')
        self.token = response.data["token"]
        self.assertEqual(response.status_code, 200)
        assert response.data['email'] == self.email
        assert response.data['username'] == self.username
        assert response.data.get("token")


