from django.urls import reverse
from authors.apps.articles.serializers import ArticleSerializer
from authors.base_test import BaseTestCase
from authors.apps.articles.models import Article
from authors.apps.comments.models import Comment
import json


class TestComments(BaseTestCase):
    """
    Testcase for user to comment on an article
    """

    def test_comment_fields_should_be_there(self):
        """test all fields required to comment on an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        data = {}
        response2 = self.client.post(url, data)
        self.assertEqual(response2.status_code, 400)
        assert(response2.data['body'][0] == "This field is required.")

    def test_user_can_comment_on_an_article(self):
        """A user should be able to add a comment to an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        self.assertEqual(response2.status_code, 201)


    def test_user_cannot_comment_on_an_invalid_article(self):
        """A user should be able to add a comment to an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': 'slug'})
        response2 = self.client.post(url, self.new_comment)
        self.assertEqual(response2.status_code, 404)
        assert(response2.data['detail'] == "Not found.")


    def test_user_can_get_one_comment_of_an_article(self):
        """A user should be able to get comments of an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        response3 = self.client.get(url)
        self.assertEqual(response3.status_code, 200)

    def test_response_of_getting_an_article_with_no_comment(self):
        """A user should be able to get a valid response when getting an article with no comments"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        assert(response2.data['Message'] == "There are no comments for this article")

    def test_user_can_edit_a_comment(self):
        """A user should be able to edit a comment to an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        data = {
            "body":"new comment"
        }
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id':response2.data['id']})
        response3 = self.client.put(url, data)
        self.assertEqual(response3.status_code, 201)

    def test_user_can_get_more_than_one_comment(self):
        """A user should be able to edit a comment to an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        data = {
            "body":"new comment"
        }
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response3 = self.client.post(url, data)
        response4 = self.client.get(url, data)
        self.assertEqual(response4.status_code, 200)

    def test_user_cannot_post_empty_comment(self):
        """A user should not be able to add an empty comment to an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        data = {
            "body":""
        }
        response2 = self.client.post(url, data)
        self.assertEqual(response2.status_code, 400)

    def test_user_can_only_edit_their_comments(self):
        """A user can only edit their comments"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        data = {
            "body":"new comment"
        }
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id':response2.data['id']})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 403)

    def test_user_can_delete_a_comment(self):
        """A user can only edit their comments"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id':response2.data['id']})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)

    def test_user_can_only_delete_their_comments(self):
        """A user can only edit their comments"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id':response2.data['id']})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_edit_a_non_existing_comment(self):
        """A user should be able to edit a comment to an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        data = {
            "body":"new comment"
        }
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id':1000})
        response3 = self.client.put(url, data)
        self.assertEqual(response3.status_code, 404)

    def test_user_can_create_a_thread(self):
        """A user should be able to thread a comment"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        data = {
            "body":"new comment"
        }
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id':response2.data['id']})
        response3 = self.client.post(url, data)
        self.assertEqual(response3.status_code, 201)

    def test_user_cannot_create_a_thread_on_a_non_existing_comment(self):
        """A user should be able to thread a comment"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        data = {
            "body":"new comment"
        }
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id':115})
        response3 = self.client.post(url, data)
        self.assertEqual(response3.status_code, 404)
        assert(response3.data['detail'] == "Not found.")

    def test_user_can_get_a_comment_with_its_thread(self):
        """test that a user can get a comment with its threads"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id':response2.data['id']})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_get_a_non_existing_comment(self):
        """test that a user can get a comment with its threads"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id':5})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404) 
        assert(response.data['detail'] == "Not found.")

    def  test_user_is_authenticated(self):
        """test that a user is authenticated"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + "mytoken")
        response = self.client.post(self.article_url, self.new_article)
        self.assertEqual(response.status_code, 403)
        assert(response.data['detail'] == "Invalid token")

    def  test_user_has_not_provided_authentication_details(self):
        """test that a user is authenticated"""
        response = self.client.post(self.article_url, self.new_article)
        self.assertEqual(response.status_code, 403)
        assert(response.data['detail'] == "Authentication credentials were not provided.")

    def test_user_can_get_previous_history_of_a_comment(self):
        """A user should be able to get edit history ofcomments of an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id': response2.data['id']})
        response3 = self.client.put(url, self.new_comment) 
        url = reverse('comments:previous_comment', kwargs={'slug': response.data['slug'], 'id':response2.data['id']})
        response3 = self.client.get(url)
        self.assertEqual(response3.status_code, 200)

    def test_user_cannot_get_edit_history_of_a_non_existing_comment(self):
        """A user should not be able to get edit histories of a non-existing comment"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        data = {
            "body":"edited comment"
        }
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment) 
        url = reverse('comments:previous_comment', kwargs={'slug': response.data['slug'], 'id':115})
        response3 = self.client.get(url)
        self.assertEqual(response3.status_code, 404)
        assert(response3.data['Message'] == "Either the comment does not exist or it has not been edited before")

    def test_user_can_get_complete_edit_history_of_a_comment(self):
        """A user should be able to get edit histories of comments of an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id': response2.data['id']})
        response3 = self.client.put(url, self.new_comment) 
        url = reverse('comments:all_previous_comments', kwargs={'slug': response.data['slug'], 'id':response2.data['id']})
        response3 = self.client.get(url)
        self.assertEqual(response3.status_code, 200)

    def test_user_cannot_get_complete_edit_history_of_a_non_existing_comment(self):
        """A user should be able to get comments of an article if it exists"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id': response2.data['id']})
        response3 = self.client.put(url, self.new_comment) 
        url = reverse('comments:all_previous_comments', kwargs={'slug': response.data['slug'], 'id':115})
        response3 = self.client.get(url)
        self.assertEqual(response3.status_code, 404)
        assert(response3.data['Message'] == "This comment does not exist")

    def test_author_is_returned_with_comments(self):
        """A user should be able to view author of a comment"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        response3 = self.client.get(url)
        assert(response3.data[0]['author']['username'] == "mike")
        self.assertEqual(response3.status_code, 200)

    


    

