from rest_framework import status
from authors.base_test import BaseTestCase


class TestProfile(BaseTestCase):
    """Test the User profile interactions"""

    profile_url = 'http://127.0.0.1:8000/api/profiles/mike'
    data_bio = {
        "bio": "I am Mike"
    }
    data_image = {
        "image": "http://kkjasfkj.ciom"
    }

    def test_update_user_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(self.profile_url, data=self.data_bio)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        assert response.data['bio'] == 'I am Mike'

    def test_modified_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client.put(self.profile_url, data=self.data_bio)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert response.data['bio'] == 'I am Mike'

    def test_upload_image_url_type(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(self.profile_url, data=self.data_image)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        print(response.data)
        assert response.data['image'] == "http://kkjasfkj.ciom"

    def test_modify_none_user_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(self.profile_url+'s', data=self.data_bio)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        assert response.data['detail'] == 'Not found.'
 