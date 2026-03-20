"""votes/urls.py"""
from django.urls import path
from . import views

app_name = 'votes'

urlpatterns = [
    path('<int:topic_pk>/cast/', views.vote_create_view, name='create'),
    path('<int:topic_pk>/update/', views.vote_update_view, name='update'),
    path('<int:topic_pk>/withdraw/', views.vote_delete_view, name='delete'),
]
