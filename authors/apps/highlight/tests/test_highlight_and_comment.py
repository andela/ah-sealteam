"""
Imports
"""
from django.urls import reverse
from authors.base_test import BaseTestCase

class HighlightTestCase(BaseTestCase):
    """
    Class that tests highlight and comment functionality
    """

    def test_user_can_highlight(self):
        """
        test case for users to highlight a text
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('highlight:highlight', kwargs={'slug': response.data['slug']})
        response_data = self.client.post(url, self.highlight_data, format='json')
        self.assertEqual(response_data.status_code, 201)

    def test_user_can_delete_highlight(self):
        """
        Test user can delete highlight
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('highlight:highlight', kwargs={'slug': response.data['slug']})
        response_data = self.client.post(url, self.highlight_data, format='json')
        url = reverse('highlight:highlights', kwargs={'slug': response.data['slug']})
        response_data = self.client.delete(url, format='json')
        self.assertEqual(response_data.status_code, 200)
        self.assertEqual(response_data.data.get('message'), 'Highlight removed successfully!')

    def test_user_cannot_delete_a_none_existing_highlight(self):
        """
        Test user cannot delete a none existing bookmark
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('highlight:highlights', kwargs={'slug': response.data['slug']})
        response_data = self.client.delete(url, format='json')
        self.assertEqual(response_data.status_code, 404)
        self.assertEqual(response_data.data.get('message'), 'This article has no such highlight')

    def test_get_highlights_for_an_article(self):
        """
        Test user gets highlights for an article
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('highlight:highlight', kwargs={'slug': response.data['slug']})
        response_data = self.client.post(url, self.highlight_data, format='json')
        get_url = reverse('highlight:highlights', kwargs={'slug': response.data['slug']})
        response_data = self.client.get(get_url, format='json')
        self.assertEqual(response_data.status_code, 200)
        
    def test_post_highlights_for_an_article_if_exists(self):
        """
        Test user posts a highlight if it already exists
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('highlight:highlight', kwargs={'slug': response.data['slug']})
        response_data = self.client.post(url, self.highlight_data, format='json')
        get_url = reverse('highlight:highlight', kwargs={'slug': response.data['slug']})
        response_data = self.client.post(get_url, self.highlight_data, format='json')
        self.assertEqual(response_data.status_code, 200)
        self.assertEqual(response_data.data.get('message'), 'Updated the highlighted text')
        
    def test_post_highlight_exists_in_an_article(self):
        """
        Test user posts highlight if exists in the article body
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('highlight:highlight', kwargs={'slug': response.data['slug']})
        response_data = self.client.post(url, self.highlight_test_data, format='json')
        self.assertEqual(response_data.status_code, 404)
        self.assertEqual(response_data.data['error'].get('message'), 'The highlighted text does not exist')
        
    def test_get_highlights_for_an_article_if_none(self):
        """
        Test user gets highlights for an article if there are highlights
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        get_url = reverse('highlight:highlights', kwargs={'slug': response.data['slug']})
        response_data = self.client.get(get_url, format='json')
        self.assertEqual(response_data.status_code, 404)
        self.assertEqual(response_data.data.get('message'), 'This article has no highlights')
