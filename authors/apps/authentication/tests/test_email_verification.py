"""This file will be used to test get user and also token"""
from authors.apps.authentication.models import User
from authors.base_test import BaseTestCase
from rest_framework import status
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse

class TestEmailVerification(BaseTestCase):

    def test_account_verification(self):
        """
        Test whether account is verified.
        """
        response = self.client.post(self.register_url, self.new_user, format='json')
        assert response.data.get("token")
        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 201)

    def test_email_verification_invalid_user(self):
        """
        Test if token used for verification is wrong
        """
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, 201)
        token = 'fgtrehcgdscdcvyetfdxdrntv'
        response1 = self.client.get('http://127.0.0.1:8000/api/activate/NA/' + token)
        self.assertEqual(response1.status_code, 200)
        assert response1.content.decode() == 'User not found'

    def test_vaerification_token_is_invalid(self):
        """This one will  try to test invalid token"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data["token"])
        user_response = self.client.get(reverse("authentication:update_user"))
        token = 'fgtrehcgdscdcvyetfdxdffg'
        uid = urlsafe_base64_encode(force_bytes(user_response.data["username"])).decode("utf-8")
        response1 = self.client.get(f'http://127.0.0.1:8000/api/activate/{uid}/{token}')        
        self.assertEqual(response1.status_code, 403)
        assert response1.data["token"] == 'Invalid token'


        # self.assertIn('<html><head><title>Wrong Link</title>', response1)
        

    def test_if_email_send_verification_link(self):
        """
        Check if email was successfully sent
        """
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data["token"])
        user_response = self.client.get(reverse("authentication:update_user"))
        token = 'fgtrehcgdscdcvyetfdxdffg'
        uid = urlsafe_base64_encode(force_bytes(user_response.data["username"])).decode("utf-8")
        response1 = self.client.get(f'http://127.0.0.1:8000/api/activate/{uid}/{response.data["token"]}')        
        self.assertEqual(response1.status_code, 200)
        assert response1.content.decode() == 'Thank you for your email confirmation. Now you can login your account.'