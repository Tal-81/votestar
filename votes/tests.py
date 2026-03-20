"""votes/tests.py"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from users.models import User
from topics.models import Topic
from .models import Vote


class VoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='voter@example.com', password='pass1234!')
        self.topic = Topic.objects.create(title='Poll', created_by=self.user)

    def test_create_vote(self):
        vote = Vote.objects.create(user=self.user, topic=self.topic, rating=4)
        self.assertEqual(vote.rating, 4)

    def test_one_vote_per_user_per_topic(self):
        Vote.objects.create(user=self.user, topic=self.topic, rating=3)
        with self.assertRaises(Exception):
            Vote.objects.create(user=self.user, topic=self.topic, rating=5)

    def test_vote_str(self):
        vote = Vote.objects.create(user=self.user, topic=self.topic, rating=5)
        self.assertIn('5★', str(vote))


class VoteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='voter@example.com', password='pass1234!')
        self.other = User.objects.create_user(email='other@example.com', password='pass1234!')
        self.topic = Topic.objects.create(title='Poll', created_by=self.other)

    def test_cast_vote(self):
        self.client.login(username='voter@example.com', password='pass1234!')
        response = self.client.post(reverse('votes:create', args=[self.topic.pk]), {'rating': 4})
        self.assertTrue(Vote.objects.filter(user=self.user, topic=self.topic).exists())

    def test_cannot_vote_twice(self):
        self.client.login(username='voter@example.com', password='pass1234!')
        self.client.post(reverse('votes:create', args=[self.topic.pk]), {'rating': 4})
        self.client.post(reverse('votes:create', args=[self.topic.pk]), {'rating': 5})
        self.assertEqual(Vote.objects.filter(user=self.user, topic=self.topic).count(), 1)

    def test_cannot_vote_on_expired_topic(self):
        self.topic.end_time = timezone.now() - timedelta(hours=1)
        self.topic.save()
        self.client.login(username='voter@example.com', password='pass1234!')
        self.client.post(reverse('votes:create', args=[self.topic.pk]), {'rating': 4})
        self.assertFalse(Vote.objects.filter(user=self.user, topic=self.topic).exists())

    def test_update_vote(self):
        self.client.login(username='voter@example.com', password='pass1234!')
        Vote.objects.create(user=self.user, topic=self.topic, rating=3)
        self.client.post(reverse('votes:update', args=[self.topic.pk]), {'rating': 5})
        vote = Vote.objects.get(user=self.user, topic=self.topic)
        self.assertEqual(vote.rating, 5)

    def test_withdraw_vote(self):
        self.client.login(username='voter@example.com', password='pass1234!')
        Vote.objects.create(user=self.user, topic=self.topic, rating=3)
        self.client.post(reverse('votes:delete', args=[self.topic.pk]))
        self.assertFalse(Vote.objects.filter(user=self.user, topic=self.topic).exists())

    def test_vote_requires_login(self):
        response = self.client.post(reverse('votes:create', args=[self.topic.pk]), {'rating': 4})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Vote.objects.exists())
