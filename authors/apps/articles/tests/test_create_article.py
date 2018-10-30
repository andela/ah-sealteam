"""
Imports
"""

from rest_framework import status
from authors.base_test import BaseTestCase

class TestCreateArticle(BaseTestCase):
    """
    Testcase for user to create an article
    """

    def test_user_create_article(self):
        """
        Testing. Can i user create an article?
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        self.assertEqual(response.status_code, 201)

    def test_get_a_single_article(self):
        """
        Testing if user can retrieve a single article
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        # import pdb; pdb.set_trace()
        response1 = self.client.get(self.article_url + '1')
        self.assertEqual(response1.status_code, 200)

    def test_get_all_artcles(self):
        """
        Testing a user can get all the articles in the application
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.article_url)
        self.assertEqual(response.status_code, 200)
