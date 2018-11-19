from rest_framework import status
from authors.base_test import BaseTestCase


class TestProfile(BaseTestCase):
    """Test the User profile getresponses"""

    profile_url = 'http://127.0.0.1:8000/api/profiles/'

    def test_get_all_profiles(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert response.data['count'] == 1
        assert response.data['next'] == None

    def test_current_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.profile_url + 'me')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert response.data['profile']['user']['username'] == 'mike'
        assert response.data['profile']['bio'] == ''
        assert response.data['profile']['image'] == None

    def test_specific_user_profile(self):
        response = self.client.get(self.profile_url + 'mike')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert response.data['profile']['bio'] == ''
        assert response.data['profile']['image'] == None
