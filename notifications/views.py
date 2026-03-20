"""notifications/views.py"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification


@login_required
def notification_list_view(request):
    """Show all notifications for the current user and mark them as read."""
    notifications = Notification.objects.filter(
        user=request.user
    ).select_related('topic', 'topic__created_by')

    # Mark all as read
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'notifications/list.html', {
        'notifications': notifications,
    })


@login_required
def notification_clear_view(request):
    """Delete all notifications for the current user."""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user).delete()
        messages.success(request, 'All notifications cleared.')
    return redirect('notifications:list')
