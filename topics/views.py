from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Topic
from .forms import TopicForm
from votes.models import Vote
from notifications.utils import maybe_create_expiry_notification


def topic_list_view(request):
    """Public list of all topics, newest first."""
    topics = (
            Topic.objects
            .select_related('created_by')
            .prefetch_related('votes')
        )
    user_votes = {}
    if request.user.is_authenticated:
        votes = (
            Vote.objects
            .filter(user=request.user).values('topic_id', 'rating')
        )
        user_votes = {v['topic_id']: v['rating'] for v in votes}
    return render(request, 'topics/list.html', {
        'topics': topics,
        'user_votes': user_votes,
    })


def topic_detail_view(request, pk):
    """Detail view for a single topic."""
    topic = get_object_or_404(
        Topic.objects.select_related('created_by').prefetch_related('votes__user'),
        pk=pk,
    )
    # Lazily create expiry notifications when topic is first viewed after expir
    if not topic.is_active:
        maybe_create_expiry_notification(topic)

    user_vote = None
    if request.user.is_authenticated:
        user_vote = topic.votes.filter(user=request.user).first()
    return render(request, 'topics/detail.html', {
        'topic': topic,
        'user_vote': user_vote,
    })


@login_required
def topic_create_view(request):
    """
    Create a new topic.
    Business rule: user can only have ONE active topic at a time.
    """
    # Check if user already has an active topic
    active_topic = Topic.objects.filter(
        created_by=request.user,
        end_time__gt=timezone.now()
    ).first()

    if active_topic:
        messages.warning(
            request,
            f'You already have an active topic: "{active_topic.title}". '
            f'Wait for it to close before creating a new one.'
        )
        return redirect('topics:detail', pk=active_topic.pk)

    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            messages.success(
                request,
                'Your topic is live! Voting is open for 72 hours.'
            )
            return redirect('topics:detail', pk=topic.pk)
    else:
        form = TopicForm()
    return render(request, 'topics/create.html', {'form': form})


@login_required
def topic_delete_view(request, pk):
    """
    Delete a topic. Only the owner can delete it.
    """
    topic = get_object_or_404(Topic, pk=pk)
    if topic.created_by != request.user:
        messages.error(request, 'You can only delete your own topics.')
        return redirect('topics:detail', pk=pk)

    if request.method == 'POST':
        title = topic.title
        topic.delete()
        messages.success(request, f'Topic "{title}" has been deleted.')
        return redirect('topics:list')

    return render(request, 'topics/delete_confirm.html', {'topic': topic})
