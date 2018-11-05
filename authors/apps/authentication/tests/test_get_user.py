"""This file will be used to test get user and also token"""
from authors.apps.authentication.models import User
from authors.base_test import BaseTestCase


class TestRetrieveUser(BaseTestCase):
    """This class will test user"""

    def test_get_user(self):
        """This will test get user"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get('/api/user', self.new_user, format='json')
        assert response.status_code == 200
        assert response.data["email"] == "testemail@gmail.com"
        assert response.data["username"] == "mike"

    def test_get_user_no_token(self):
        response = self.client.get('/api/user', self.new_user, format='json')
        assert response.status_code == 403
        assert response.data["detail"] == "Authentication credentials were not provided."

    def test_get_user_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + "jhdsbhjdsjdksjjdsjnk")
        response = self.client.get('/api/user', self.new_user, format='json')
        assert response.status_code == 403
        assert response.data["detail"] == "Invalid token"

    def test_get_doesnotexist_user(self):
        User.objects.get(email=self.email).delete()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' +self.token)
        response = self.client.get('/api/user', self.new_user, format='json')
        assert response.status_code == 403
        assert response.data["detail"] == "User does not exist"
