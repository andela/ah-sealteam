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
        data={
            "user":{
                "email":self.wrongmail,
                "username":self.username,
                "password": "ajkjndsjnsd"
            }
        }
        response = self.client.post(self.register_url,data , format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["email"][0] == "Enter a valid email address."

    def test_user_register_with_no_password(self):
        data = {
            "user": {
                "email": self.email,
                "username": self.username,
                "password":""
            }
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["password"][0] == "This field may not be blank."

    def test_user_register_with_no_email(self):
        data = {
            "user": {
                "email": "",
                "username": self.username,
                "password": "sgdssdhbd"
            }
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["email"][0] == "This field may not be blank."

    def test_register_if_user_already_exists(self):
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assert response.data['email'] == "asheuh@gmail.com"
        assert response.data['username'] == "asheuh"
        assert response.data.get("token")
        response = self.client.post(self.register_url, self.new_user, format='json')
        # import pdb;pdb.set_trace()
        assert response.status_code==400
        assert response.data["errors"]["email"][0] == "user with this email already exists."
        assert response.data["errors"]["username"][0] == "user with this username already exists."
