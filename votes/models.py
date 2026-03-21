"""
Each user can vote once per topic (unique_together enforces this at DB level).
Rating must be 1–5. The 72h lock is enforced in the view layer.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from topics.models import Topic


class Vote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # delete user → delete their votes
        related_name='votes',
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,  # delete topic → delete its votes
        related_name='votes',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # DB-level guarantee: one vote per user per topic
        unique_together = ('user', 'topic')
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'{self.user.email} → {self.topic.title}: {self.rating}★'
        )
