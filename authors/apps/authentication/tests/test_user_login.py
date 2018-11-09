"Test the login endpoint"
from authors.apps.authentication.models import User
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
                "email": self.email,
                "password": self.password
            }
        response = self.client.post(self.login_url, data, )
        self.assertEqual(response.status_code, 200)
        assert response.data.get("token")

    def test_user_login_with_invalid_password(self):
        """
        Test with wrong password
        :return:
        """
        data = {
                "email": self.email,
                "password": "ndssjdknkjf"
            }
        response = self.client.post(self.login_url, data, )
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["error"][0] == "A user with this email " \
                                                      "and password was not found."

    #
    def test_user_login_with_no_email(self):
        """
        Test with no email
        :return:
        """
        data = {
                "email": "",
                "password": "ndssjdknkjf"
            }
        response = self.client.post(self.login_url, data, )
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["email"][0] == "This field may not be blank."

    #
    def test_user_login_with_no_password(self):
        """Test with no password"""
        data = {
                "email": self.email,
                "password": ""
            }
        response = self.client.post(self.login_url, data, )
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["password"][0] == "This field may not be blank."

    #
    def test_user_login_without_an_account(self):
        """Login without account"""
        data = {
                "email": "noaccount@fma.com",
                "password": "ndssjdknkjf"
            }
        response = self.client.post(self.login_url, data, )
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["error"][0] == "A user with this email " \
                                                      "and password was not found."

    #
    def test_user_login_with_deactivated_account(self):
        """Login deactivated user"""
        user = User.objects.get(email=self.email)
        user.is_active = False
        user.save()
        response = self.client.post(self.login_url, self.data_for_get_test, )
        self.assertEqual(response.status_code, 400)
        assert response.data['errors']["error"][0] == "A user with this email " \
                                                      "and password was not found."
