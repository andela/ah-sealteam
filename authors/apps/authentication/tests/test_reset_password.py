"""THis module is used to test user"""
from rest_framework import status

from authors.base_test import BaseTestCase


class TestUserResetPassword(BaseTestCase):
    """
    This class creates test for user reset password functionality
    """

    

    def test_forgot_password_request_with_valid_email(self):
        """test that user can request for password with valid email"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {
            "email": self.email
        }
        response = self.client.post(self.forgot_password_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        assert response.data['message'] == "A link has been successfully sent to your email." \
                    " Check your spam folder incase you don't find it."


    def test_forgot_password_request_with_invalid_email(self):
        """test that user cannot request for password with invalid email"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {
            "email": "wrongemail@gmail.com"
        }
        response = self.client.post(self.forgot_password_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']['error'][0] == "No records found with the email address." \
                                                      " Create An Account To Continue."


    def test_forgot_password_request_with_no_email(self):
        """test that user cannot request for password without an email"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {
            "email": " "
        }
        response = self.client.post(self.forgot_password_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']['email'][0] == "This field may not be blank."

    def test_forgot_password_request_with_no_email_field(self):
        """test that user cannot request for password without an email"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {}
        response = self.client.post(self.forgot_password_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']['email'][0] == "This field is required."


    def test_reset_password_with_invalid_token(self):
        """test that user cannot reset password with an invalid email"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {
            "email": self.email
        }
        response = self.client.post(self.forgot_password_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        assert response.data['message'] == "A link has been successfully sent to your email." \
                    " Check your spam folder incase you don't find it."
        token = "generated_token"
        currentsite_domain = '127.0.0.1:8000'
        reset_link = 'http://' + currentsite_domain + '/api/users/resetpassword/{}/'.format(token)
        data = {
            "new_password":"newpassword",
	        "confirm_password":"newpassword",
	        "email":self.email
        }
        response = self.client.post(reset_link, data, format='json')
        self.assertEqual(response.status_code, 400)
        


    def test_reset_passwords_match(self):
        """test that reset passwords should be the same"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {
            "email": self.email
        }
        response = self.client.post(self.forgot_password_url, data, format='json')
        token = "generated_token"
        currentsite_domain = '127.0.0.1:8000'
        reset_link = 'http://' + currentsite_domain + '/api/users/resetpassword/{}/'.format(token)
        data = {
            "new_password":"newpassword",
	        "confirm_password":"newpass1",
	        "email":self.email
        }
        response = self.client.post(reset_link, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['error'][0] == "Passwords do not match."


    def test_reset_passwords_must_be_valid(self):
        """test that reset passwords must be valid"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {
            "email": self.email
        }
        response = self.client.post(self.forgot_password_url, data, format='json')
        token = "generated_token"
        currentsite_domain = '127.0.0.1:8000'
        reset_link = 'http://' + currentsite_domain + '/api/users/resetpassword/{}/'.format(token)
        data = {
            "new_password":"newpass",
	        "confirm_password":"newpass",
	        "email":self.email
        }
        response = self.client.post(reset_link, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['new_password'][0] == "Ensure this field has at least 8 characters."


    def test_reset_password_form_is_rendered(self):
        """test that form to reset password can be rendered"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {
            "email": self.email
        }
        response = self.client.post(self.forgot_password_url, data, format='json')
        token = "generated_token"
        currentsite_domain = '127.0.0.1:8000'
        reset_link = 'http://' + currentsite_domain + '/api/users/resetpassword/{}/'.format(token)
        data = {
            "new_password":"newpass",
	        "confirm_password":"newpass",
	        "email":self.email
        }
        response = self.client.get(reset_link, data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_request_with_invalid_data(self):
        """test that user can request for password with valid email"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = self.email
        response = self.client.post(self.forgot_password_url, data, format='json')
        self.assertEqual(response.status_code, 400)
    

    def test_reset_passwords_with_invalid_data(self):
        """test that reset passwords should be the same"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {
            "email": self.email
        }
        response = self.client.post(self.forgot_password_url, data, format='json')
        token = "generated_token"
        currentsite_domain = '127.0.0.1:8000'
        reset_link = 'http://' + currentsite_domain + '/api/users/resetpassword/{}/'.format(token)
        data = "new_password"
        response = self.client.post(reset_link, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_reset_passwords_with_no_email(self):
        """test that reset passwords must be valid"""
        response = self.client.post(self.register_url, self.new_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {
            "email": self.email
        }
        response = self.client.post(self.forgot_password_url, data, format='json')
        token = "generated_token"
        currentsite_domain = '127.0.0.1:8000'
        reset_link = 'http://' + currentsite_domain + '/api/users/resetpassword/{}/'.format(token)
        data = {
            "new_password":"newpass123",
	        "confirm_password":"newpass123",
	        "email":" "
        }
        response = self.client.post(reset_link, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['email'][0] == "This field may not be blank."

    
       
    

        




