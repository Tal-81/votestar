"""topics/tests.py"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from users.models import User
from .models import Topic


class TopicModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='pass1234!')

    def test_end_time_is_72h_after_creation(self):
        topic = Topic.objects.create(title='Test', created_by=self.user)
        delta = topic.end_time - topic.created_at
        self.assertAlmostEqual(delta.total_seconds(), 72 * 3600, delta=5)

    def test_is_active_true_for_new_topic(self):
        topic = Topic.objects.create(title='Active', created_by=self.user)
        self.assertTrue(topic.is_active)

    def test_is_active_false_for_expired_topic(self):
        topic = Topic.objects.create(title='Expired', created_by=self.user)
        topic.end_time = timezone.now() - timedelta(hours=1)
        topic.save()
        self.assertFalse(topic.is_active)

    def test_ordering_newest_first(self):
        t1 = Topic.objects.create(title='First', created_by=self.user)
        t2 = Topic.objects.create(title='Second', created_by=self.user)
        topics = list(Topic.objects.all())
        self.assertEqual(topics[0], t2)

    def test_average_rating_none_when_no_votes(self):
        topic = Topic.objects.create(title='No votes', created_by=self.user)
        self.assertIsNone(topic.average_rating)


class TopicViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='pass1234!')
        self.topic = Topic.objects.create(title='Test Topic', created_by=self.user)

    def test_topic_list_public(self):
        response = self.client.get(reverse('topics:list'))
        self.assertEqual(response.status_code, 200)

    def test_topic_detail_public(self):
        response = self.client.get(reverse('topics:detail', args=[self.topic.pk]))
        self.assertEqual(response.status_code, 200)

    def test_create_requires_login(self):
        response = self.client.get(reverse('topics:create'))
        self.assertEqual(response.status_code, 302)

    def test_create_topic(self):
        self.client.login(username='test@example.com', password='pass1234!')
        # First expire the existing topic so we can create a new one
        self.topic.end_time = timezone.now() - timedelta(hours=1)
        self.topic.save()
        response = self.client.post(reverse('topics:create'), {
            'title': 'New Topic',
            'description': 'A description',
        })
        self.assertTrue(Topic.objects.filter(title='New Topic').exists())

    def test_cannot_create_when_active_topic_exists(self):
        self.client.login(username='test@example.com', password='pass1234!')
        response = self.client.post(reverse('topics:create'), {
            'title': 'Another Topic',
            'description': '',
        })
        # Should redirect back, not create new topic
        self.assertFalse(Topic.objects.filter(title='Another Topic').exists())

    def test_only_owner_can_delete(self):
        other = User.objects.create_user(email='other@example.com', password='pass1234!')
        self.client.login(username='other@example.com', password='pass1234!')
        response = self.client.post(reverse('topics:delete', args=[self.topic.pk]))
        self.assertTrue(Topic.objects.filter(pk=self.topic.pk).exists())
