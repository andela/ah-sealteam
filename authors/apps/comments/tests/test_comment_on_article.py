from django.urls import reverse

from authors.base_test import BaseTestCase


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


    def test_user_can_get_comments_of_an_article(self):
        """A user should be able to get comments of an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        
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


    def test_user_can_delete_a_comment(self):
        """A user should be able to delete a comment to an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        response2 = self.client.post(url, self.new_comment)
        url = reverse('comments:update_comment', kwargs={'slug': response.data['slug'], 'id':response2.data['id']})
        response3 = self.client.delete(url)
        self.assertEqual(response3.status_code, 200)

    def test_user_cannot_post_empty_comment(self):
        """A user should not be able to add an empty comment to an article"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article)
        url = reverse('comments:comment_article', kwargs={'slug': response.data['slug']})
        data = {
            "body":""
        }
        response2 = self.client.post(url, data, )
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
        response = self.client.post(self.article_url, self.new_article, )
        self.assertEqual(response.status_code, 403)
        assert(response.data['detail'] == "Invalid token")
