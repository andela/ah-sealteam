"""
Imports
"""
from django.urls import reverse
from authors.base_test import BaseTestCase


class TestCreateArticle(BaseTestCase):
    """
    Testcase for user to create an article
    """

    def test_user_is_authenticated(self):
        """
        Testing if a user is authenticated
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + "token")
        response = self.client.post(self.article_url, self.new_article, )
        self.assertEqual(response.status_code, 403)

    def test_user_create_article(self):
        """
        Testing. Can a user create an article?
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        self.assertEqual(response.status_code, 201)

    def test_article_fields_are_present(self):
        """
        Testing if all fields are included
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        data = {

        }
        response = self.client.post(self.article_url, data, )
        self.assertEqual(response.status_code, 400)

    def test_article_title_cannot_be_empty(self):
        """
        Testing if all fields are included
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        data = {
            "title":" ",
	        "description":"another",
	        "tags":["one"],
	        "body":"another"
        }
        response = self.client.post(self.article_url, data, )
        self.assertEqual(response.status_code, 400)
        assert(response.data['title'][0] == "This field may not be blank.")
   

    def test_get_a_single_article(self):
        """
        Testing if user can retrieve a single article
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        response1 = self.client.get(self.article_url + 'bmsdshdkskdskdsdshdk-ksdjsdksjdkshd-dkshdkshds')
        self.assertEqual(response1.status_code, 200)

    def test_get_a_non_existing_article(self):
        """
        Testing if user can retrieve a single article
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        response1 = self.client.get(self.article_url + 'article')
        self.assertEqual(response1.status_code, 404)

    def test_get_all_artcles(self):
        """
        Testing a user can get all the articles in the application
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.article_url)
        self.assertEqual(response.status_code, 200)

    def test_user_can_update_articles(self):
        """
        Given a user and an article, the user should be able to update an article.
        """
        data = {
            "title": "This is an update of the title",
            "description": "THis is an update to a description",
            "body": "This is an update to a body"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        url = reverse('articles:retrieve_article', kwargs={'slug': response.data['slug']})
        response1 = self.client.put(url, data)
        self.assertEqual(response1.status_code, 200)

    def test_user_can_only_update_their_articles(self):
        """
        Given a user and an article, the user should be able to update an article.
        """
        data = {
            "title": "This is an update of the title",
            "description": "THis is an update to a description",
            "body": "This is an update to a body"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        url = reverse('articles:retrieve_article', kwargs={'slug': response.data['slug']})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 403)
        assert(response.data['detail'] == "You are now allowed to access edit or delete")

    def test_user_cannot_update_a_non_existing_article(self):
        """
        Given a user and an article, the user should be able to update an article.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        url = reverse('articles:retrieve_article', kwargs={'slug': response.data['slug']})
        response1 = self.client.put(url, "article")
        self.assertEqual(response1.status_code, 400)

    def test_user_can_delete_an_article(self):
        """
        Given a user and an article, the user should be able to delete their article
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        url = reverse('articles:retrieve_article', kwargs={'slug': response.data['slug']})
        response1 = self.client.delete(url)
        self.assertEqual(response1.data['message'], {'Article was deleted successful'})
        self.assertEqual(response1.status_code, 200)

    def test_user_can_only_delete_their_own_article(self):
        """
        Given a user and an article, the user should be able to delete their article
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        url = reverse('articles:retrieve_article', kwargs={'slug': response.data['slug']})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(url)
        self.assertEqual(response.data['message'], {'Article was deleted successful'})
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_delete_a_non_existing_article(self):
        """
        Given a user and an article, the user should be able to delete their article
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        url = reverse('articles:retrieve_article', kwargs={'slug': 'slug'})
        response1 = self.client.delete(url)
        self.assertEqual(response1.status_code, 404)
        assert(response1.data['detail'] == "Not found.")



