import json
import os
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.contrib.sites.models import Site
from django.urls import reverse

from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.facebook.provider import GRAPH_API_URL
import responses

from rest_framework import status

from .mixins import TestsMixin

class TestSocialAuth(TestsMixin, TestCase):

    USERNAME = 'person'
    PASS = 'person'
    EMAIL = "person1@world.com"
    REGISTRATION_DATA = {
        "username": USERNAME,
        "password1": PASS,
        "password2": PASS,
        "email": EMAIL
    }
    @classmethod
    def setUpTestData(cls):
        """
        init social apps for social auth testing
        """
        cls.site = Site.objects.create(
            domain="localhost:8000",
            name="localhost"
        )

        cls.facebook_social_app = SocialApp.objects.create(
            provider='facebook',
            name='Facebook',
            client_id=os.getenv("FB_CLIENT_ID"),
            secret=os.getenv("FB_CLIENT_SECRET")
        )

        cls.twitter_social_app = SocialApp.objects.create(
            provider='twitter',
            name='Twitter',
            client_id=os.getenv("TW_CLIENT_ID"),
            secret=os.getenv("TW_CLIENT_SECRET")
        )

        cls.google_social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=os.getenv("GG_CLIENT_ID"),
            secret=os.getenv("GG_CLIENT_SECRET")
        )
        
        cls.twitter_social_app.sites.add(cls.site)
        cls.facebook_social_app.sites.add(cls.site)
        cls.google_social_app.sites.add(cls.site)

    def setUp(self):
        self.init()
        # import pdb;pdb.set_trace()
        self.graph_api_url = GRAPH_API_URL + '/me'
        self.twitter_url = 'http://twitter.com/foobarme'

    @responses.activate
    @override_settings(SITE_ID=2)
    def test_failed_social_auth(self):
        # fake response
        responses.add(
            responses.GET,
            self.graph_api_url,
            body='',
            status=400,
            content_type='application/json'
        )

        payload = {
            'access_token': 'abc123'
        }

        self.post(self.fb_login_url, data=payload, status_code=400)

    @responses.activate
    @override_settings(SITE_ID=2)
    def test_facebook_auth(self):
        # fake response for facebook call
        resp_body = {
            "id": "123123123123",
            "email": "John@email.com",
            "username": "john.smith",
        }

        responses.add(
            responses.GET,
            self.graph_api_url,
            body=json.dumps(resp_body),
            status=200,
            content_type='application/json'
        )

        users_count = get_user_model().objects.all().count()
        payload = {
            'access_token': 'EAAB2PCmXF4QBAECwSwCAJfiSYZBVIluNBquGIZAxc3ALA7ahC8F4XfoD7QPKdOAEK8GZCrGspKS8obosgmyySTTCsLZCpQAYTEsMt7fxxqDkZC28BJeL3r7yrOkJjTmIsbtr5aNfCOyLIFGbNIWYqnxfCIla0GwBNY3Ct6treazZB37Ka0ktqzR4dCMTozLLaNEGzaSlTCgMDJTpc4UMZAJ'
        }

        self.post(self.fb_login_url, data=payload, status_code=200)
        # test that a new user has been created
        self.assertEqual(get_user_model().objects.all().count(), users_count + 1)

        # make sure that second request will not create a new user
        self.post(self.fb_login_url, data=payload, status_code=200)
        self.assertEqual(get_user_model().objects.all().count(), users_count + 1)

    def _twitter_social_auth(self):
        # fake response for twitter call
        resp_body = {
            "id": "123123123123",
        }

        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/account/verify_credentials.json',
            body=json.dumps(resp_body),
            status=200,
            content_type='application/json'
        )

        users_count = get_user_model().objects.all().count()
        payload = {
            'access_token': '290602078-r8rczQNFYQxixUCSjZ4oi2qAUx1gRQpyvX37Pw0W',
            'token_secret': 'BuAPJIe4xbZo10YT0SzN0ETnJEWRTwYYlJtSHZsMmWpKp'
        }

        self.post(self.tw_login_url, data=payload)
        # test that a new user has been created
        self.assertEqual(get_user_model().objects.all().count(), users_count + 1)

        # make sure that second request will not create a new user
        self.post(self.tw_login_url, data=payload, status_code=200)

        self.assertEqual(get_user_model().objects.all().count(), users_count + 1)

    @responses.activate
    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True, SITE_ID=2)
    def test_twitter_social_auth(self):
        self._twitter_social_auth()

    @responses.activate
    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False, SITE_ID=2)
    def test_twitter_social_auth_without_auto_singup(self):
        self._twitter_social_auth()

    @responses.activate
    @override_settings(SITE_ID=2)
    def test_twitter_social_auth_request_error(self):
        # fake response for twitter call
        resp_body = {
            "id": "123123123123",
        }

        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/account/verify_credentials.json',
            body=json.dumps(resp_body),
            status=400,
            content_type='application/json'
        )

        users_count = get_user_model().objects.all().count()
        payload = {
            'access_token': 'abc123',
            'token_secret': '1111222233334444'
        }

        self.post(self.tw_login_url, data=payload, status_code=400)

        self.assertEqual(get_user_model().objects.all().count(), users_count)
