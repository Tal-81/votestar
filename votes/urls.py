from django.urls import path
from . import views

app_name = 'votes'

urlpatterns = [
    path('topics/<int:topic_pk>/vote/', views.vote_create_view, name='create'),
    path('topics/<int:topic_pk>/vote/edit/', views.vote_update_view, name='update'),
    path('topics/<int:topic_pk>/vote/remove/', views.vote_delete_view, name='delete'),
]
