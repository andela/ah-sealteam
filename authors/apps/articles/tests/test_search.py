from authors.base_test import BaseTestCase


class TestSearch(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.response_article = self.client.post(self.article_url,
                                                self.new_article)

    def test_get_user_questions(self):
        response = self.client.get(self.article_url+"?username=mike")
        assert response.data["count"] == 1

    def test_get_by_tag(self):
        response = self.client.get(self.article_url+"?tag=sdjsdsdhd")
        assert response.data["count"] == 1

    def test_get_by_keyword(self):
        response = self.client.get(self.article_url+
                                   "?search=bmsdshdkskdskdsdshdk")
        assert response.data["count"] == 1

    def test_get_search_by_filter(self):
        response = self.client.get(self.article_url+
                                   "?search=bmsdshdkskdskdsdshdk?"
                                   "username=mike?tag=sdjsdsdhd")
        assert response.data["count"] == 1
