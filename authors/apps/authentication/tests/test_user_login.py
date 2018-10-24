from authors.base_test import BaseTestCase
import pytest
class TestUserLogin(BaseTestCase):
    """
    This class logs in a user who has an account in the application
    params: [email, password]
    """
    
    @pytest.mark.skip(reason="no way of currently testing this")
    def test_user_login(self):
        with self.client:
            pass

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_user_login_with_invalid_password(self):
        with self.client:
            pass
    @pytest.mark.skip(reason="no way of currently testing this")
    def test_user_login_with_no_email(self):
        with self.client:
            pass
    @pytest.mark.skip(reason="no way of currently testing this")
    def test_user_login_with_no_password(self):
        with self.client:
            pass
    @pytest.mark.skip(reason="no way of currently testing this")
    def test_user_login_without_an_account(self):
        with self.client:
            pass
    @pytest.mark.skip(reason="no way of currently testing this")
    def test_user_login_with_deactivated_account(self):
        with self.client:
            pass
