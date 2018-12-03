# from authors.base_test import BaseTestCase
# from django.urls import reverse

# class TestFavorite(BaseTestCase):
#     """
#     Class will test favorite and un favoriting an article
#     """
#     def setUp(self):
#         """
#         Will provide data for testing purposes
#         """
#         super().setUp()
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
#         response = self.client.post(self.article_url, self.new_article, format='json')
#         slug = response.data["slug"]
#         self.url = reverse('articles:favorite_article', kwargs={"slug": slug})

#     def test_article_not_found(self):
#         """
#         This will test if an article exist
#         """
#         pass

#     def test_favorite_article(self):
#         """
#         Test favorite method if it works
#         """
#         pass

#     def test_unfavorite_article(self):
#         """
#         Test if the unfavoriting article method is working 
#         """
#         pass

    