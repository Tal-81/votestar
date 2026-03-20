"""
users/models.py
Custom User model using email as the unique identifier instead of username.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager: email is the unique identifier, not username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model.
    - email is unique and used for login
    - username is removed (we set it to email on save)
    - CASCADE delete removes topics and votes automatically via FK
    """
    username = None                         # Remove the default username field
    email = models.EmailField(unique=True)  # Email is the login credential

    USERNAME_FIELD = 'email'        # Use email for authentication
    REQUIRED_FIELDS = []            # No extra required fields for createsuperuser

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    @property
    def display_name(self):
        """Return first name if set, otherwise email prefix."""
        return self.first_name or self.email.split('@')[0]
