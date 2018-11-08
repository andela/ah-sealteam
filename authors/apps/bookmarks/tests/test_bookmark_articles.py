"""
imports
"""

from django.urls import reverse
from authors.base_test import BaseTestCase

class TestBookmark(BaseTestCase):
    """
    The test cases for bookmarking an article
    """
    def test_user_can_bookmark_article(self):
        """
        Test user can bookmark
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('bookmarks:bookmarks', kwargs={'slug': response.data['slug']})
        response_data = self.client.post(url, format='json')
        self.assertEqual(response_data.status_code, 201)
        self.assertEqual(response_data.data.get('message'), 'bookmarked')

    def test_user_can_delete_bookmarked_article(self):
        """
        Test user can delete bookmark
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('bookmarks:bookmarks', kwargs={'slug': response.data['slug']})
        response_data = self.client.post(url, format='json')
        response_data = self.client.delete(url, format='json')
        self.assertEqual(response_data.status_code, 200)
        self.assertEqual(response_data.data.get('message'), 'Successfully removed from bookmark')

    def test_user_cannot_delete_a_none_existing_bookmark(self):
        """
        Test user cannot delete a none existing bookmark
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('bookmarks:bookmarks', kwargs={'slug': response.data['slug']})
        response_data = self.client.delete(url, format='json')
        self.assertEqual(response_data.status_code, 404)
        self.assertEqual(response_data.data.get('message'), 'This article has not been bookmarked')

    def test_user_trying_to_bookmark_an_article_that_is_not_found(self):
        """
        Test user bookmarking aa article that does not exist
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        url = reverse('bookmarks:bookmarks', kwargs={'slug': 'this-is-a-slug'})
        response_data = self.client.delete(url, format='json')
        self.assertEqual(response_data.status_code, 404)
        self.assertEqual(response_data.data.get('message'), 'Article not found')

    def test_anonymous_user_bookmarking_an_article(self):
        """
        Test for anonymous users trying to bookmark an artcle
        """
        url = reverse('bookmarks:bookmarks', kwargs={'slug': 'this-is-a-slug'})
        response_data = self.client.post(url, format='json')
        self.assertEqual(response_data.status_code, 403)

    def test_bookmarking_already_bookmrked__article(self):
        """
        Test user bookmarking an already bookmarked article
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('bookmarks:bookmarks', kwargs={'slug': response.data['slug']})
        response_data = self.client.post(url, format='json')
        response_data = self.client.post(url, format='json')
        self.assertEqual(response_data.status_code, 400)

    def test_get_bookmarked_articles(self):
        """
        Test user bookmarking an already bookmarked article
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('bookmarks:bookmarks', kwargs={'slug': response.data['slug']})
        response_data = self.client.post(url, format='json')
        get_url = reverse('bookmarks:all_bookmarks')
        response_data = self.client.get(get_url, format='json')
        self.assertEqual(response_data.status_code, 200)
