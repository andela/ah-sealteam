from rest_framework import status
from authors.base_test import BaseTestCase


class TestProfile(BaseTestCase):
    """Test the follow/unfolow functionality"""

    friend_url = 'http://127.0.0.1:8000/api/profiles'

    def test_follow_other_user(self):
        self.client.post('http://127.0.0.1:8000/api/users/',
                         data=self.new_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.friend_url + '/asheuh/follow')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert response.data['username'] == 'asheuh'

    def test_unfollow_other_user(self):
        self.client.post('http://127.0.0.1:8000/api/users/',
                         data=self.new_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.friend_url + '/asheuh/follow')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert response.data['username'] == 'asheuh'
        response1 = self.client.delete(self.friend_url + '/asheuh/unfollow')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        assert response1.data['username'] == 'asheuh'

    def test_follow_self(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.friend_url + '/mike/follow')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        assert response.data['message'] == 'You cannot follow yourself'

    def test_follow_none_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.friend_url + '/mike1/follow')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        assert response.data['detail'] == 'Not found.'

    def test_unfollow_self(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(self.friend_url + '/mike/unfollow')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        assert response.data['message'] == 'You cannot unfollow yourself'

    def test_unfollow_none_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(self.friend_url + '/mike1/unfollow')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        assert response.data['detail'] == 'Not found.'

    def test_get_followers(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.friend_url + '/mike/followers')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert response.data["count"] == 0

    def test_get_followers_for_none_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.friend_url + '/mike1/followers')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        assert response.data['detail'] == 'Not found.'

    def test_get_following(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.friend_url + '/mike/following')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert response.data["count"] == 0

    def test_get_following_for_none_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.friend_url + '/mike1/following')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        assert response.data['detail'] == 'Not found.'
