"""notifications/admin.py"""
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'is_read', 'created_at', 'message']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__email', 'topic__title']
    readonly_fields = ['created_at']
