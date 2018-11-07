"""This file will be used to test get user and also token"""
from authors.apps.authentication.models import User
from authors.base_test import BaseTestCase

class TestEmailVerification(BaseTestCase):
    def test_emailverification(self):
        user = User.objects.create_user(email='vichchanga@gmail.com',
                                   password="hbjasjbds5jds", username="usernamr")
