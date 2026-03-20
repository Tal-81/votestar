"""users/tests.py"""
from django.test import TestCase, Client
from django.urls import reverse
from .models import User


class UserModelTest(TestCase):
    def test_create_user_with_email(self):
        user = User.objects.create_user(email='test@example.com', password='pass1234!')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('pass1234!'))
        self.assertFalse(user.is_staff)

    def test_email_is_unique(self):
        User.objects.create_user(email='unique@example.com', password='pass1234!')
        with self.assertRaises(Exception):
            User.objects.create_user(email='unique@example.com', password='pass1234!')

    def test_display_name_uses_first_name(self):
        user = User(email='john@example.com', first_name='John')
        self.assertEqual(user.display_name, 'John')

    def test_display_name_falls_back_to_email_prefix(self):
        user = User(email='john@example.com')
        self.assertEqual(user.display_name, 'john')

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email='admin@example.com', password='admin1234!')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class UserViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='pass1234!')

    def test_register_page_loads(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user(self):
        response = self.client.post(reverse('users:register'), {
            'email': 'newuser@example.com',
            'password1': 'strongpass123!',
            'password2': 'strongpass123!',
        })
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_login_success(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'test@example.com',
            'password': 'pass1234!',
        })
        self.assertRedirects(response, reverse('topics:list'))

    def test_profile_requires_login(self):
        response = self.client.get(reverse('users:profile'))
        self.assertRedirects(response, f"/users/login/?next=/users/profile/")

    def test_delete_account(self):
        self.client.login(username='test@example.com', password='pass1234!')
        response = self.client.post(reverse('users:delete_account'))
        self.assertFalse(User.objects.filter(email='test@example.com').exists())


class SuperuserProtectionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            email='admin@example.com', password='admin1234!'
        )
        self.normal_user = User.objects.create_user(
            email='user@example.com', password='pass1234!'
        )

    def test_superuser_cannot_delete_own_account_via_view(self):
        """Superuser hitting DELETE view should be redirected, not deleted."""
        self.client.login(username='admin@example.com', password='admin1234!')
        response = self.client.post(reverse('users:delete_account'))
        # Account must still exist
        self.assertTrue(User.objects.filter(email='admin@example.com').exists())

    def test_superuser_redirected_to_profile_on_delete_attempt(self):
        """Superuser should be redirected to profile with error message."""
        self.client.login(username='admin@example.com', password='admin1234!')
        response = self.client.post(reverse('users:delete_account'))
        self.assertRedirects(response, reverse('users:profile'))

    def test_superuser_delete_page_redirects_on_get(self):
        """Even GET request to delete page should redirect superuser away."""
        self.client.login(username='admin@example.com', password='admin1234!')
        response = self.client.get(reverse('users:delete_account'))
        self.assertRedirects(response, reverse('users:profile'))

    def test_normal_user_can_still_delete_account(self):
        """Normal users should still be able to delete their accounts."""
        self.client.login(username='user@example.com', password='pass1234!')
        self.client.post(reverse('users:delete_account'))
        self.assertFalse(User.objects.filter(email='user@example.com').exists())
