"""notifications/urls.py"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list_view, name='list'),
    path('clear/', views.notification_clear_view, name='clear'),
]
