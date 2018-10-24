from authors.base_test import BaseTestCase

class TestUserRegistration(BaseTestCase):
    """
    This class creates test for user register functionality
    Params: [username, email, password]
    """
    def test_user_creates_account(self):
        with self.client:
            pass

    def test_user_register_with_invalid_email(self):
        with self.client:
            pass

    def test_user_register_with_no_password(self):
        with self.client:
            pass

    def test_user_register_with_no_email(self):
        with self.client:
            pass

    def test_register_if_user_already_exists(self):
        with self.client:
            pass
