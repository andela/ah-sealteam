from authors.base_test import BaseTestCase
from django.urls import reverse
from rest_framework import status
from authors.apps.authentication.models import User
from rest_framework.test import force_authenticate, APIRequestFactory

class TestFavorite(BaseTestCase):
    """
    Class will test favorite and un favoriting an article
    """

    def test_favorite_article(self):
        """
        Test favorite method if it works
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('favorites:article_favorite', kwargs={'slug': response.data['slug']})
        result_data = self.client.post(url, format='json')
        self.assertEqual(result_data.status_code, 200)
        

    def test_unfavorite_article(self):
        """
        Test if the unfavoriting article method is working 
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('favorites:article_favorite', kwargs={'slug': response.data['slug']})
        post_response_data = self.client.post(url, format='json')
        post_response_data1 = self.client.post(url, format='json')
        self.assertEqual(post_response_data.status_code, 200)

    
    def test_get_favorited_articles(self):
        """
        Test if method to get all favorited articles works
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        url = reverse('favorites:article_favorite', kwargs={'slug': response.data['slug']})
        response_data = self.client.post(url, format='json')
        get_url = 'http://127.0.0.1:8000/api/articles/favorites/'
        response_data = self.client.get(get_url, format='json')
        self.assertEqual(response_data.status_code, 200)


    

    