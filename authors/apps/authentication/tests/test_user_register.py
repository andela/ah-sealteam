"""THis module is used to test user"""
from rest_framework import status
from django.contrib.auth import get_user_model
from authors.base_test import BaseTestCase

class UserTest(BaseTestCase):

    def test_create_user(self):
        self.assertIsInstance(
            get_user_model().objects.create_user(**self.new_user), get_user_model())

    def test_create_super_user(self):
        user = get_user_model().objects.create_superuser(**self.new_user)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

class TestUserRegistration(BaseTestCase):
    """
    This class creates test for user register functionality
    Params: [username, email, password]
    """

    def test_user_creates_account(self):
        """
        Ensures user can create a new account
        """
        response = self.client.post(self.register_url, self.new_user, )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assert response.data.get("token")

    def test_user_register_with_invalid_email(self):
        """
        register with wrong email
        :return:
        """
        data = {
            "email": self.wrongmail,
            "username": self.username,
            "password": "ajkjndsj4nsd"
        }
        response = self.client.post(self.register_url, data, )
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["email"][0] == "Enter a valid email address."

    def test_user_register_with_no_password(self):
        """
        Register with no password
        :return:
        """
        data = {
            "email": self.email,
            "username": self.username,
            "password": ""
        }
        response = self.client.post(self.register_url, data, )
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["password"] == "Please provide a password"

    def test_user_register_with_no_email(self):
        """
        Register with no email
        :return:
        """
        data = {
            "email": "",
            "username": self.username,
            "password": "sgds6sdhbd"
        }
        response = self.client.post(self.register_url, data, )
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["email"] == "Please provide an email"

    def test_user_register_with_no_username(self):
            """
            Register with no email
            :return:
            """
            data = {
                "email": self.email,
                "username": "",
                "password": "sgds6sdhbd"
            }
            response = self.client.post(self.register_url, data, format='json')
            self.assertEqual(response.status_code, 400)
            assert response.data['errors']["username"] == "Please provide a an username"

    def test_password_no_digit(self):
        """Try to register with password with no digit"""
        my_user = {
            "email": "newmail@gmail.com",
            "username": "mineuser",
            "password": "asghvdbjknfsadnkf"
        }
        response = self.client.post(self.register_url, my_user, )
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["password"] == "Password must be between 8 - 20 " \
                                                      "characters and at least 1 digit"

    def test_register_if_user_already_exists(self):
        """Register with register user"""
        response = self.client.post(self.register_url, self.new_user, )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assert response.data.get("token")
        response = self.client.post(self.register_url, self.new_user, )
        assert response.status_code == 400
        assert response.data["errors"]["email"][0] == "user with this email already exists."

        assert response.data["errors"]["username"][0] == "user with this username already exists."
        
