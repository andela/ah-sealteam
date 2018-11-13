"""
This module tests comment like and dislike functionality
"""
from django.urls import reverse
from authors.base_test import BaseTestCase
from authors.apps.likedislike.models import LikeDislike

class TestLikeDislikeComment(BaseTestCase):
    """
    Testcase for user to like and/or dislike a comment
    """

    def test_like_a_comment(self):
        """
        Test than an authenticated user can like an comment
        """
        # create a new article
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        self.assertEqual(response.status_code, 201)
        slug = response.data.get("slug")
        url = reverse('comments:comment_article', kwargs={'slug':slug})
        response2 = self.client.post(url, self.new_comment)
        self.assertEqual(response2.status_code, 201)
        comment_id = response2.data['id']
        like_url = reverse("comments:comment_like", kwargs={"slug":slug,"id":comment_id})
        response2 = self.client.post(like_url)
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(response2.data.get("like_count"), 1)
        # when a user likes the same comment twice, his like should be removed.
        response3 = self.client.post(like_url)
        self.assertEqual(response3.status_code, 201)
        self.assertEqual(response3.data.get("like_count"), 0)

    def test_dislike_a_comment(self):
        """
        Test than an authenticated user can dislike an comment
        """
        # create a new article
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        self.assertEqual(response.status_code, 201)
        slug = response.data.get("slug")
        url = reverse('comments:comment_article', kwargs={'slug':slug})
        response2 = self.client.post(url, self.new_comment)
        # create new comment
        self.assertEqual(response2.status_code, 201)
        comment_id = response2.data['id']
        dislike_url = reverse("comments:comment_dislike", kwargs={"slug":slug,"id":comment_id})
        response2 = self.client.post(dislike_url)
        liked_comment = self.client.get(reverse("comments:update_comment",
                                        kwargs={"slug":slug,"id":comment_id}))
        self.assertEqual(liked_comment.data['votes']["sum_rating"], -1)
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(response2.data.get("dislike_count"), 1)
        # when a user dislikes the same comment twice, his dislike should be removed.
        response3 = self.client.post(dislike_url)
        self.assertEqual(response3.status_code, 201)
        self.assertEqual(response3.data.get("dislike_count"), 0)

    def test_like_dislike_a_comment(self):
        """
        Test than an authenticated user cannot 
        like and dislike the same comment at the same time
        """
        # create a new article
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        self.assertEqual(response.status_code, 201)
        slug = response.data.get("slug")
        url = reverse('comments:comment_article', kwargs={'slug':slug})
        # create new comment
        response2 = self.client.post(url, self.new_comment)
        self.assertEqual(response2.status_code, 201)
        comment_id = response2.data['id']
        like_url = reverse("comments:comment_like", kwargs={"slug":slug,"id":comment_id})
        response2 = self.client.post(like_url)
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(response2.data.get("like_count"), 1)
        # when a user dislikes the same comment like should be removed.
        dislike_url = reverse("comments:comment_dislike", kwargs={"slug":slug,"id":comment_id})
        response3 = self.client.post(dislike_url)
        self.assertEqual(response3.status_code, 201)
        self.assertEqual(response3.data.get("dislike_count"), 1)
        self.assertEqual(response3.data.get("like_count"), 0)
