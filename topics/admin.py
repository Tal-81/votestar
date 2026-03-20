"""topics/admin.py"""
from django.contrib import admin
from .models import Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'end_time', 'is_active', 'vote_count']
    list_filter = ['created_at']
    search_fields = ['title', 'created_by__email']
    readonly_fields = ['created_at', 'end_time']
    ordering = ['-created_at']
