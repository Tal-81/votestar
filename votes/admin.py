"""votes/admin.py"""
from django.contrib import admin
from .models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'rating', 'created_at', 'updated_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__email', 'topic__title']
    readonly_fields = ['created_at', 'updated_at']
