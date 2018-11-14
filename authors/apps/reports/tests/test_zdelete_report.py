from authors.base_test import BaseTestCase


class TestProfile(BaseTestCase):
    """Test the report articles"""
    report_url = 'http://127.0.0.1:8000/api/articles/'

    report = {
        'reason': 'The article violates this and that'
    }

    def test_delete_specific_report(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        self.client.post(self.report_url + response.data['slug'] + '/report' , self.report, format='json')
        response = self.client.delete(self.report_url + 'reports/5')
        self.assertEqual(response.data,None)