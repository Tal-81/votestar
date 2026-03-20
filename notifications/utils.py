"""
notifications/utils.py
Helper to create expiry notifications for a topic.
Called from topic detail view when the topic is first detected as expired.
Uses get_or_create so it's safe to call multiple times (idempotent).
"""
from .models import Notification


def maybe_create_expiry_notification(topic):
    """
    Create notifications when a topic expires:
      1. Owner notification
      2. All voters notification
    Uses get_or_create per user so it never duplicates.
    """
    if topic.is_active:
        return  # Don't create notifications for active topics

    # Gather recipients: owner + all voters
    recipients = {topic.created_by}
    for vote in topic.votes.select_related('user'):
        recipients.add(vote.user)

    for user in recipients:
        if user == topic.created_by:
            msg = f'Your topic "{topic.title}" has closed. It received {topic.vote_count} vote(s).'
            if topic.average_rating:
                msg += f' Average rating: {topic.average_rating}★'
        else:
            msg = f'A topic you voted on has closed: "{topic.title}".'

        Notification.objects.get_or_create(
            user=user,
            topic=topic,
            defaults={'message': msg},
        )
