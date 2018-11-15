"""
Imports
"""
from django.urls import reverse
from authors.base_test import BaseTestCase


class TestCreateArticle(BaseTestCase):
    """
    Testcase for statistics
    """

    def setUp(self):
        super().setUp()
        self.stats_url_article = reverse("stats:my_article_stacs")
        self.stats_url_reading = reverse("stats:my_reading_stacs")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.first_article = {
            'title': 'This is is my article',
            'description': 'this is descriiption',

            'body': 'this is the bofy',
            'tags': ['politics']
        }
        self.third_article = {
            'title': 'This is is my article second',
            'description': 'this is descriiption second',

            'body': 'this is the bofy third',
            'tags': ['work']
        }
        # post the articles by two users
        article1_rest = self.client.post(self.article_url, self.new_article,
                                         format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        article2_rest = self.client.post(self.article_url, self.first_article,
                                         format='json')
        article3_rest = self.client.post(self.article_url, self.third_article,
                                         format='json')

        # get articles
        self.client.get(reverse('articles:retrieve_article',
                                kwargs={"slug": article1_rest.data["slug"]}))
        self.client.get(reverse('articles:retrieve_article',
                                kwargs={"slug": article2_rest.data["slug"]}))
        self.client.get(reverse('articles:retrieve_article',
                                kwargs={"slug": article3_rest.data["slug"]}))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client.get(reverse('articles:retrieve_article',
                                kwargs={"slug": article1_rest.data["slug"]}))
        self.client.get(reverse('articles:retrieve_article',
                                kwargs={"slug": article2_rest.data["slug"]}))
        self.client.get(reverse('articles:retrieve_article',
                                kwargs={"slug": article3_rest.data["slug"]}))
        self.client.get(reverse('articles:retrieve_article',
                                kwargs={"slug": article3_rest.data["slug"]}))

    def test_get_my_article_stats(self):
        """this will check statistics of my articles"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response = self.client.get(self.stats_url_article)
        assert response.status_code == 200
        data = response.data
        assert data["count"] == 2
        assert data["results"][0]['reads']["no_read"] == 2
        assert data["results"][0]['reads'].get("read_last_at")

    def test_get_reading_statistics(self):
        """This are the statistics of articles i have read"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response = self.client.get(self.stats_url_reading)
        assert response.status_code == 200
        data = response.data
        assert data["count"] == 3
        assert data["results"][0]["no_read"] == 1
        assert data["results"][0].get("read_last_at")
        assert data["results"][0].get("article")
