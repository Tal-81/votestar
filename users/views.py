"""users/views.py"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('topics:list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.display_name}! Your account has been created.')
            return redirect('topics:list')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('topics:list')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'topics:list')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('users:login')
    return render(request, 'users/logout_confirm.html')


@login_required
def profile_view(request):
    user = request.user
    topics = user.topics.order_by('-created_at')
    votes = user.votes.select_related('topic').order_by('-created_at')
    return render(request, 'users/profile.html', {
        'topics': topics,
        'votes': votes,
    })


@login_required
def delete_account_view(request):
    """
    Delete the user account.
    Business rules:
      - Superuser accounts (is_superuser=True) can NEVER be deleted,
        not even by the superuser themselves.
      - CASCADE deletes topics and votes automatically for normal users.
    """
    # ── Block superuser deletion ──────────────────────────────────────────────
    if request.user.is_superuser:
        messages.error(request, 'Admin accounts cannot be deleted. Contact your system administrator.')
        return redirect('users:profile')

    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()   # FK CASCADE handles topics and votes
        messages.success(request, 'Your account has been permanently deleted.')
        return redirect('users:login')
    return render(request, 'users/delete_account.html')
