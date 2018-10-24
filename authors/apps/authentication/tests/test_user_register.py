"""THis module is used to test user"""
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
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assert response.data['email'] == "asheuh@gmail.com"
        assert response.data['username'] == "asheuh"
        assert response.data.get("token")

    def test_user_register_with_invalid_email(self):
        """
        register with wrong email
        :return:
        """
        data = {
            "user": {
                "email": self.wrongmail,
                "username": self.username,
                "password": "ajkjndsjns5d"
            }
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["email"][0] == "Enter a valid email address."

    def test_user_register_with_no_password(self):
        """
        Register with no password
        :return:
        """
        data = {
            "user": {
                "email": self.email,
                "username": self.username,
                "password": ""
            }
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["password"][0] == "This field may not be blank."

    def test_user_register_with_no_email(self):
        """
        Register with no email
        :return:
        """
        data = {
            "user": {
                "email": "",
                "username": self.username,
                "password": "sgds6sdhbd"
            }
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["email"][0] == "This field may not be blank."

    def test_password_no_digit(self):
        """Try to register with password with no digit"""
        my_user = {
            "user": {
                "email": "newmail@gmail.com",
                "username": "mineuser",
                "password": "asghvdbjknfsadnkf"
            }
        }
        response = self.client.post(self.register_url, my_user, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["password"][0] == "Password should contain at least a digit"

    def test_register_if_user_already_exists(self):
        """Register with register user"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assert response.data['email'] == "asheuh@gmail.com"
        assert response.data['username'] == "asheuh"
        assert response.data.get("token")
        response = self.client.post(self.register_url, self.new_user, format='json')
        assert response.status_code == 400
        assert response.data["errors"]["email"][0] == "user with this email already exists."
        assert response.data["errors"]["username"][0] == "user with this username already exists."
