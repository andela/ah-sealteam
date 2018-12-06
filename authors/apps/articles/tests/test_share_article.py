from authors.base_test import BaseTestCase
from django.urls import reverse

class TestShareArticle(BaseTestCase):
    """
    Class will test sharing an article via email
    """

    def test_share_article(self):
        """
        Test share article via email works.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        response1 = self.client.post('http://127.0.0.1:8000/api/articles/{}/share'.format(response.data['slug']), {
        "article": {
            "share_with": "jlsnyule22@gmail.com"
        }
    })
        self.assertEqual(response1.data['message'],  "Article shared successfully")
        self.assertEqual(response1.status_code, 200)