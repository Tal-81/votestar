"""config/urls.py — Root URL configuration"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('topics.urls', namespace='topics')),
    path('users/', include('users.urls', namespace='users')),
    path('votes/', include('votes.urls', namespace='votes')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
]
