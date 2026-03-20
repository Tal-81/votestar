"""
votes/views.py
All vote mutations go through POST-only views (no GET forms needed).
Business rules enforced here:
  - 72h window (topic.is_active)
  - one vote per user per topic (unique_together + get_or_create)
  - only owner can update/delete their own vote
"""
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from topics.models import Topic
from .models import Vote
from .forms import VoteForm
from notifications.utils import maybe_create_expiry_notification


def _get_active_topic_or_error(pk, request):
    """Helper: fetch topic and check it's still open. Returns (topic, error_bool)."""
    topic = get_object_or_404(Topic, pk=pk)
    if not topic.is_active:
        messages.error(request, 'Voting is closed — this topic has expired.')
        return topic, True
    return topic, False


@login_required
def vote_create_view(request, topic_pk):
    """Cast a new vote. POST only."""
    if request.method != 'POST':
        return redirect('topics:detail', pk=topic_pk)

    topic, has_error = _get_active_topic_or_error(topic_pk, request)
    if has_error:
        return redirect('topics:detail', pk=topic_pk)

    # Check user hasn't already voted
    if Vote.objects.filter(user=request.user, topic=topic).exists():
        messages.warning(request, 'You have already voted on this topic.')
        return redirect('topics:detail', pk=topic_pk)

    form = VoteForm(request.POST)
    if form.is_valid():
        vote = form.save(commit=False)
        vote.user = request.user
        vote.topic = topic
        vote.save()
        messages.success(request, f'You rated this {vote.rating}★ — thanks for voting!')
    else:
        messages.error(request, 'Invalid rating. Please choose 1–5 stars.')

    return redirect('topics:detail', pk=topic_pk)


@login_required
def vote_update_view(request, topic_pk):
    """Update an existing vote. POST only."""
    if request.method != 'POST':
        return redirect('topics:detail', pk=topic_pk)

    topic, has_error = _get_active_topic_or_error(topic_pk, request)
    if has_error:
        return redirect('topics:detail', pk=topic_pk)

    vote = get_object_or_404(Vote, user=request.user, topic=topic)
    form = VoteForm(request.POST, instance=vote)
    if form.is_valid():
        form.save()
        messages.success(request, f'Vote updated to {vote.rating}★')
    else:
        messages.error(request, 'Invalid rating. Please choose 1–5 stars.')

    return redirect('topics:detail', pk=topic_pk)


@login_required
def vote_delete_view(request, topic_pk):
    """Withdraw (delete) a vote. POST only."""
    if request.method != 'POST':
        return redirect('topics:detail', pk=topic_pk)

    topic, has_error = _get_active_topic_or_error(topic_pk, request)
    if has_error:
        return redirect('topics:detail', pk=topic_pk)

    vote = get_object_or_404(Vote, user=request.user, topic=topic)
    vote.delete()
    messages.success(request, 'Your vote has been withdrawn.')
    return redirect('topics:detail', pk=topic_pk)
