"""notifications/context_processors.py
Injects unread notification count into every template context.
"""
from .models import Notification


def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
