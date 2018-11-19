from authors.base_test import BaseTestCase


class TestProfile(BaseTestCase):
    """Test the report articles"""
    report_url = 'http://127.0.0.1:8000/api/articles/'

    report = {
        'reason': 'The article violates this and that'
    }

    def test_report_own_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        response1 = self.client.post(self.report_url + response.data['slug'] + '/report' , self.report, format='json')
        self.assertEqual(response1.data['message'], 'You cannot report your own article')

    def test_report_other_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response1 = self.client.post(self.report_url + response.data['slug'] + '/report' , self.report, format='json')
        self.assertEqual(response1.data['sender']['username'], 'newuser')

    def test_get_all_reports(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response1 = self.client.get(self.report_url + 'reports/all' , self.report, format='json')
        self.assertEqual(response1.data['detail'], 'You do not have permission to perform this action.')

    def test_get_specific_report(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response0 = self.client.post(self.report_url + response.data['slug'] + '/report' , self.report, format='json')
        self.assertEqual(response0.data['sender']['username'], 'newuser')
        response1 = self.client.get(self.report_url + 'reports/2')
        self.assertEqual(response1.data['sender']['username'], 'newuser')

    def test_get_own_reports(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response1 = self.client.post(self.report_url + response.data['slug'] + '/report' , self.report, format='json')
        self.assertEqual(response1.data['sender']['username'], 'newuser')
        response2 = self.client.get(self.report_url + 'reports/my_reports')
        self.assertEqual(response2.data['count'], 1)
        self.assertIn('bmsdsh', response2.data['results'][0]['reported_article']['title'])

    def test_update_specific_report(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.article_url, self.new_article, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)
        response1 = self.client.post(self.report_url + response.data['slug'] + '/report' , self.report, format='json')
        self.assertEqual(response1.data['sender']['username'], 'newuser')
        response2 = self.client.put(self.report_url + 'reports/4' , self.report, format='json')
        self.assertEqual(response2.data['sender']['username'], 'newuser')

