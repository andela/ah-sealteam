"""
test module for notifications

"""

import json

from notifications.signals import notify
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

# local imports
from authors.base_test import BaseTestCase
from authors.apps.articles.models import Article
from authors.apps.comments.models import Comment

class BaseNotificationsTestCase(BaseTestCase):
    DEFAULT_NOTIFICATION_COUNT = 10
    URLS = {
        'all': reverse("notifications:all-notifications"),
        'sent': reverse("notifications:sent-notifications"),
        'unsent': reverse("notifications:unsent-notifications"),
        'read': reverse("notifications:read-notifications"),
        'unread': reverse("notifications:unread-notifications")
    }
    def create_notifications(self):
        """
        create notification instances
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        user = get_user_model().objects.get(email=self.second_test_data["email"])
        resp = self.client.post(self.article_url, data=self.new_article)
        slug = resp.data.get("slug")
        article = Article.objects.get(slug=slug)
        resp = self.client.post(reverse("comments:comment_article",
                                        kwargs={"slug":slug}),
                                        data=self.new_comment)
        # import pdb;pdb.set_trace()
        comment = Comment.objects.get(id=resp.data.get("id"))
        notify.send(user, recipient=user, verb="verb", target=article, description="description")
        notify.send(article, recipient=user, verb="verb", target=user, description="description", resource_url="url")
        notify.send(comment, recipient=user, verb="verb", target=user, description="description")
        notify.send(user, recipient=user, verb="verb", target=comment, description="description")
        
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.create_notifications()
        self.notification_type = "all"

    def get(self, notification_type=None):
        """
        Return a list of notifications and response_code
        """
        response = self.client.get(self.URLS[notification_type or self.notification_type])
        return response.status_code, json.loads(response.content)

    def delete(self, notification_type=None):
        """
        Delete a list of notifications and return the response
        """
        response = self.client.delete(self.URLS[notification_type or self.notification_type])
        return response.status_code, json.loads(response.content)
    
    def send_notification(self, user=None, verb="sample", description="You have a notification"):
        """
        Helper method to send notification to a particular user
        """
        user = user or self.test_user
        notify.send(user, recipient=user, verb=verb, description=description)

    def send_many_notifications(self, user=None, count=DEFAULT_NOTIFICATION_COUNT):
        """
        Helper method to send many notifications
        """
        for i in range(0, count):
            self.send_notification(user)


class AllNotificationsTestCase(BaseNotificationsTestCase):

    def setUp(self):
        super().setUp()
        self.send_many_notifications()

    def test_get_all_notifications(self):
        """
        Test can list all the notifications in the system
        """
        response_code, data = self.get()
        self.assertEqual(response_code, status.HTTP_200_OK)
        self.assertEqual(data['data']['count'], self.DEFAULT_NOTIFICATION_COUNT)

    def test_delete_all_notifications(self):
        """
        Test that can delete all the notifications
        """
        status_code, data = self.delete()
        self.assertEqual(status_code, status.HTTP_200_OK)
        status_code, data = self.get()
        self.assertEqual(data['data']['count'], 0)


class UnsentNotificationsTestCase(BaseNotificationsTestCase):

    def setUp(self):
        super().setUp()
        self.notification_type = "unsent"

    def test_notifications_first_unsent(self):
        """
        Ensure the notification status begins as unsent
        :return:
        """
        self.send_many_notifications()
        status_code, data = self.get()
        self.assertEqual(data['data']['count'], self.DEFAULT_NOTIFICATION_COUNT)


class SentNotificationTestCase(BaseNotificationsTestCase):

    def setUp(self):
        super().setUp()
        self.notification_type = "sent"

    def test_notifications_sent_once_queried(self):
        """
        Notifications should be marked as sent once they are retrieved
        :return:
        """
        self.send_many_notifications()
        status_code, data = self.get()
        self.assertEqual(data['data']['count'], 0)

        # get all notifications
        self.get(notification_type="all")

        # now check whether they exist in the sentbox
        status_code, data = self.get()
        self.assertEqual(data['data']['count'], self.DEFAULT_NOTIFICATION_COUNT)


class UnReadNotificationTestCase(BaseNotificationsTestCase):
    def setUp(self):
        super().setUp()
        self.notification_type = "unread"

    def notifications_unread_once_created(self):
        """
        Notifications should be unread by default
        :return:
        """
        self.send_many_notifications()
        status_code, data = self.get()
        self.assertEqual(data['data']['count'], self.DEFAULT_NOTIFICATION_COUNT)


class ReadNotificationsTestCase(BaseNotificationsTestCase):
    def setUp(self):
        super().setUp()
        self.notification_type = "read"

    def read_notifications(self, data):
        notifications = data['data']['notifications']
        if len(notifications) != 1:
            for notification in data['data']['notifications']:
                self.client.put(
                    reverse("notifications:read-notification", kwargs={'pk': notification['id']})
                )
        else:
            return self.client.put(
                reverse("notifications:read-notification", kwargs={'pk': notifications[0]['id']})
            )

    def test_can_read_notification(self):
        """
        Ensure a notification can be marked as read
        :return:
        """
        self.send_notification()
        status_code, data = self.get(notification_type='unread')
        # mark the notification as read
        response = self.read_notifications(data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        status_code, data = self.get()
        self.assertEqual(data['data']['count'], 1)

    def test_can_get_read_notifications(self):
        """
        Ensure notifications after read can be queried
        :return:
        """
        self.send_many_notifications()

        status_code, data = self.get(notification_type='unread')
        self.read_notifications(data=data)

        status_code, data = self.get()
        self.assertEqual(data['data']['count'], self.DEFAULT_NOTIFICATION_COUNT)


class NotificationSubscriptionTestCase(BaseNotificationsTestCase):

    def subscribe_to_all(self):
        """
        Helper method to subscribe to all notifications
        """
        return self.client.post(reverse("notifications:subscribe"), data={})

    def test_user_can_unsubscribe_from_app_notifications(self):
        """
        Ensure a user can opt out of app notifications
        """
        response = self.client.put(reverse("notifications:app-unsubscribe"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertIn(b'You have successfully unsubscribed to our notifications.', response.content)

    def test_user_can_unsubscribe_from_email_notifications(self):
        """
        Ensure a user can opt out email notifications
        """
        response = self.client.get(reverse("notifications:email-unsubscribe", kwargs={"token":self.token}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_subscribe_back_to_the_notifications(self):
        """
        Ensure after subscription, a user can get back to subscription
        """
        response = self.client.post(reverse("notifications:subscribe"), data={})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertIn(b'You have successfully subscribed from our notifications.', response.content)
