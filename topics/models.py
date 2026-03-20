"""
topics/models.py
A Topic is a poll. Business rules enforced here and in views:
  - end_time = created_at + 72h (auto-set in save())
  - only one active topic per user (enforced in form/view)
  - immutable after creation (no edit view provided)
  - CASCADE delete via FK to User
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Topic(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,       # delete user → delete their topics
        related_name='topics',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(editable=False)  # set automatically

    class Meta:
        ordering = ['-created_at']      # newest first

    def save(self, *args, **kwargs):
        # Auto-set end_time = created_at + 72 hours on first save
        if not self.pk:
            self.end_time = timezone.now() + timedelta(hours=72)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    # ── Computed properties used in templates ─────────────────────────────────

    @property
    def is_active(self):
        """Voting is open if we haven't reached end_time yet."""
        return timezone.now() < self.end_time

    @property
    def time_remaining(self):
        """Human-readable time left, or 'Closed'."""
        if not self.is_active:
            return 'Closed'
        delta = self.end_time - timezone.now()
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        if hours > 0:
            return f'{hours}h {minutes}m remaining'
        return f'{minutes}m remaining'

    @property
    def average_rating(self):
        """Average vote rating, or None if no votes."""
        votes = self.votes.all()
        if not votes.exists():
            return None
        total = sum(v.rating for v in votes)
        return round(total / votes.count(), 1)

    @property
    def vote_count(self):
        return self.votes.count()
