from django.urls import reverse
from rest_framework import status
from authors.base_test import BaseTestCase

class TestUserRegistration(BaseTestCase):
    """
    This class creates test for user register functionality
    Params: [username, email, password]
    """
    def test_user_creates_account(self):
        """
        Ensures user can create a new account
        """
        with self.client:
            url = reverse('create_user')
            response = self.client.post(url, self.new_user, format='json')
            self.assertEqual(response.status, status.HTTP_201_CREATED)

    def test_user_register_with_invalid_email(self):
        with self.client:
            pass

    def test_user_register_with_no_password(self):
        with self.client:
            pass

    def test_user_register_with_no_email(self):
        with self.client:
            pass

    def test_register_if_user_already_exists(self):
        with self.client:
            pass
