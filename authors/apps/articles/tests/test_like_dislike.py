"""
This module tests like and dislike functionality
"""
from django.urls import reverse
from authors.base_test import BaseTestCase
from authors.apps.articles.models import LikeDislike

class TestLikeDislikeArticle(BaseTestCase):
    """
    Testcase for user to like and/or dislike an article
    """

    def test_like_an_article(self):
        """
        Test than an authenticated user can like an article
        """
        # create a new article
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        self.assertEqual(response.status_code, 201)
        slug = response.data.get("slug")
        like_url = reverse("articles:article_like", kwargs={"slug":slug})
        response2 = self.client.post(like_url, )
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(response2.data.get("like_count"), 1)
        # when a user likes the same article twice, his like should be removed.
        response3 = self.client.post(like_url, )
        self.assertEqual(response3.status_code, 201)
        self.assertEqual(response3.data.get("like_count"), 0)

    def test_dislike_an_article(self):
        """
        Test than an authenticated user can dislike an article
        """
        # create a new article
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        self.assertEqual(response.status_code, 201)
        slug = response.data.get("slug")
        dislike_url = reverse("articles:article_dislike", kwargs={"slug":slug})
        response2 = self.client.post(dislike_url, )
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(response2.data.get("dislike_count"), 1)
        # when a user dislikes the same article twice, his dislike should be removed.
        response3 = self.client.post(dislike_url, )
        self.assertEqual(response3.status_code, 201)
        self.assertEqual(response3.data.get("dislike_count"), 0)

    def test_like_dislike_an_article(self):
        """
        Test than an authenticated user can only like or dislike an article
        """
        # create a new article
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        self.assertEqual(response.status_code, 201)
        slug = response.data.get("slug")
        dislike_url = reverse("articles:article_dislike", kwargs={"slug":slug})
        response2 = self.client.post(dislike_url, )
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(response2.data.get("dislike_count"), 1)
        # when a user likes an article that had disliked, his change should be reflected
        response3 = self.client.post(
            reverse("articles:article_like", kwargs={"slug": slug}), )
        self.assertEqual(response3.status_code, 201)
        self.assertEqual(response3.data.get("like_count"), 1)
        self.assertEqual(response3.data.get("dislike_count"), 0)
