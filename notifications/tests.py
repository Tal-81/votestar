"""notifications/tests.py"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from users.models import User
from topics.models import Topic
from votes.models import Vote
from .models import Notification
from .utils import maybe_create_expiry_notification


class NotificationModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@example.com', password='pass1234!')
        self.voter = User.objects.create_user(email='voter@example.com', password='pass1234!')
        self.topic = Topic.objects.create(title='Poll', created_by=self.owner)

    def test_no_notifications_for_active_topic(self):
        maybe_create_expiry_notification(self.topic)
        self.assertEqual(Notification.objects.count(), 0)

    def test_notifications_created_for_expired_topic(self):
        self.topic.end_time = timezone.now() - timedelta(hours=1)
        self.topic.save()
        Vote.objects.create(user=self.voter, topic=self.topic, rating=4)
        maybe_create_expiry_notification(self.topic)
        # Owner + voter should each get a notification
        self.assertEqual(Notification.objects.count(), 2)

    def test_notifications_not_duplicated(self):
        self.topic.end_time = timezone.now() - timedelta(hours=1)
        self.topic.save()
        maybe_create_expiry_notification(self.topic)
        maybe_create_expiry_notification(self.topic)  # call again
        self.assertEqual(Notification.objects.count(), 1)  # only owner, no voters

    def test_notification_marked_read_on_list_view(self):
        self.topic.end_time = timezone.now() - timedelta(hours=1)
        self.topic.save()
        maybe_create_expiry_notification(self.topic)
        client = Client()
        client.login(username='owner@example.com', password='pass1234!')
        client.get(reverse('notifications:list'))
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 0)


class NotificationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='user@example.com', password='pass1234!')
        self.topic = Topic.objects.create(title='Poll', created_by=self.user)

    def test_list_requires_login(self):
        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_loads(self):
        self.client.login(username='user@example.com', password='pass1234!')
        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(response.status_code, 200)

    def test_clear_notifications(self):
        Notification.objects.create(user=self.user, topic=self.topic, message='Test')
        self.client.login(username='user@example.com', password='pass1234!')
        self.client.post(reverse('notifications:clear'))
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 0)
