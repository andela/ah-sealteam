"Test the login endpoint"
from authors.base_test import BaseTestCase


class TestUserLogin(BaseTestCase):
    """
    This class logs in a user who has an account in the application
    params: [email, password]
    """

    def test_user_login(self):
        """
        test login
        :return:
        """
        data = {
            "user": {
                "email": self.email,
                "password": self.password
            }
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        assert response.data['email'] == self.email
        assert response.data['username'] == self.username
        assert response.data.get("token")

    def test_user_login_with_invalid_password(self):
        """
        Test with wrong password
        :return:
        """
        data = {
            "user": {
                "email": self.email,
                "password": "ndssjdknkjf"
            }
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["error"][0] == "A user with this email " \
                                                      "and password was not found."

    def test_user_login_with_no_email(self):
        """
        Test with no email
        :return:
        """
        data = {
            "user": {
                "email": "",
                "password": "ndssjdknkjf"
            }
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["email"][0] == "This field may not be blank."

    def test_user_login_with_no_password(self):
        """Test with no password"""
        data = {
            "user": {
                "email": self.email,
                "password": ""
            }
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["password"][0] == "This field may not be blank."

    def test_user_login_without_an_account(self):
        """Login without account"""
        data = {
            "user": {
                "email": "noaccount@fma.com",
                "password": "ndssjdknkjf"
            }
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["error"][0] == "A user with this email " \
                                                      "and password was not found."

    def test_user_login_with_deactivated_account(self):
        """Login deactivated user"""
        pass



