"""topics/urls.py"""
from django.urls import path
from . import views

app_name = 'topics'

urlpatterns = [
    path('', views.topic_list_view, name='list'),
    path('topics/create/', views.topic_create_view, name='create'),
    path('topics/<int:pk>/', views.topic_detail_view, name='detail'),
    path('topics/<int:pk>/delete/', views.topic_delete_view, name='delete'),
]
