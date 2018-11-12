"""This will be used to test ratings"""
from django.urls import reverse
from rest_framework.test import APIClient

from authors.base_test import BaseTestCase


class TestPostRating(BaseTestCase):
    """We need two user, one to post article and another to rate"""

    def base_method(self):
        """This one will allow our default user to post an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, )
        slug = response.data["slug"]
        self.rate_data = {"rate": 5, "comment": "I like this article"}
        self.url = reverse('articles:create_get_rating', kwargs={"slug": slug})

    def rate_user(self):
        """This user will assist us in Ratings"""
        response = self.client.post(self.register_url, self.new_user, )
        return response.data["token"]

    def base_post_rate(self):
        """This class will act as base for get, update, delete one article"""
        self.base_method()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.rate_user())
        self.rate_response = self.client.post(self.url, self.rate_data, )
        self.rate_article_url = reverse('articles:get_update_delete_rating',
                                        kwargs={"rate_id": self.rate_response.data["id"]})

    def test_posting_rating(self):
        """This one will test rating"""
        user_rate_token = self.rate_user()
        self.base_method()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user_rate_token)
        rate_response = self.client.post(self.url, self.rate_data, )
        assert rate_response.status_code == 201
        assert rate_response.data["user"] == "asheuh"
        assert rate_response.data["rate"] == 5
        assert rate_response.data["comment"] == "I like this article"

    def test_rating_your_article(self):
        """Checking if an author is trying himself"""
        self.base_method()
        rate_response = self.client.post(self.url, self.rate_data, )
        assert rate_response.status_code == 403
        assert rate_response.data["detail"] == "You are not allowed to rate yourself"

    def test_rating_no_vote(self):
        """Will test ration without ratings"""
        user_rate_token = self.rate_user()
        self.base_method()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user_rate_token)
        self.rate_data = {"rate": '', "comment": "I like this article"}
        rate_response = self.client.post(self.url, self.rate_data, )
        assert rate_response.status_code == 400
        assert rate_response.data["rate"][0] == "Acceptable values are [5, 4, 3, 2, 1]."

    def test_user_rating_twice(self):
        """This will test user trying to rate twice"""
        user_rate_token = self.rate_user()
        self.base_method()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user_rate_token)
        rate_response = self.client.post(self.url, self.rate_data, )
        assert rate_response.status_code == 201
        assert rate_response.data["user"] == "asheuh"
        assert rate_response.data["rate"] == 5
        assert rate_response.data["comment"] == "I like this article"
        rate_response = self.client.post(self.url, self.rate_data, )
        assert rate_response.status_code == 400
        assert rate_response.data["errors"][0] == 'Not allowed to rate twice.' \
                                                  ' Consider updating your rating'

    def test_user_not_authenticated(self):
        """This function will try, tating non authenticated"""

        user_rate_token = self.rate_user()
        self.base_method()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user_rate_token)
        client = APIClient()
        rate_response = client.post(self.url, self.rate_data, format='json')
        assert rate_response.status_code == 403
        assert rate_response.data["detail"] == "Authentication credentials were not provided."

    def test_404_ratings_id(self):
        """Test rate not found article"""
        user_rate_token = self.rate_user()
        self.base_method()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + user_rate_token)
        rating_post_get = reverse('articles:create_get_rating', kwargs={"slug": 'does-not-exist'})
        rate_response = self.client.post(rating_post_get, self.rate_data, )
        assert rate_response.status_code == 404
        assert rate_response.data["detail"] == "Not found."

    def test_get_ratings(self):
        """Will test getting all ratings for article"""
        self.base_method()
        response = self.client.get(self.url, format='json')
        assert response.status_code == 200

    def test_get_average(self):
        """Test average of rating of an article"""
        self.base_method()
        response = self.client.get(self.url + '?rate=average', format='json')
        assert response.status_code == 200
        assert response.data["average"] is None

    def test_get_rate(self):
        """test getting one rate"""
        self.base_post_rate()
        response = self.client.get(self.rate_article_url, format='json')
        assert response.status_code == 200
        assert response.data["user"] == "asheuh"
        assert response.data["rate"] == 5
        assert response.data["comment"] == "I like this article"

    def test_get_one_404(self):
        """Test getting one rating that is not there"""
        rate_article_url = reverse('articles:get_update_delete_rating',
                                   kwargs={"rate_id": 1000})
        response = self.client.get(rate_article_url, format='json')
        assert response.status_code == 404
        assert response.data["detail"] == "Not found."

    def test_update_rating(self):
        """Will test updating rating"""
        self.base_post_rate()
        self.rate_data = {"rate": 2, "comment": "I found better"}
        response = self.client.put(self.rate_article_url, self.rate_data, format='json')
        assert response.status_code == 200
        assert response.data["user"] == 'asheuh'
        assert response.data["rate"] == 2
        assert response.data["comment"] == 'I found better'

    def test_delete_rate(self):
        """Will test deleting a rate"""
        self.base_post_rate()
        response = self.client.delete(self.rate_article_url, format='json')
        assert response.status_code == 200
        assert response.data["message"] == 'Your rate was successfully deleted'

    def test_update_someone_rating(self):
        """Will test updating rate from authorised user"""
        self.base_post_rate()
        self.rate_data = {"rate": 2, "comment": "I found better"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(self.rate_article_url, self.rate_data, format='json')
        assert response.status_code == 403
        assert response.data["detail"] == 'You are not allowed to edit or delete this rate'

    def test_delete_someone_rating(self):
        """Try deleting with authorised used"""
        self.base_post_rate()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(self.rate_article_url, format='json')
        assert response.status_code == 403
        assert response.data["detail"] == 'You are not allowed to edit or delete this rate'
