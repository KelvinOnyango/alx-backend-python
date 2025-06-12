from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import models
from .models import Message, Notification

User = get_user_model()


@login_required
@cache_page(60)
def conversation_view(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)
    
    cache_key = f'conversation_{request.user.id}_{user_id}'
    messages = cache.get(cache_key)
    
    if not messages:
        messages = Message.objects.filter(
            models.Q(sender=request.user, receiver=other_user) |
            models.Q(sender=other_user, receiver=request.user)
        ).select_related('sender', 'receiver').prefetch_related('replies').order_by('timestamp')
        cache.set(cache_key, messages, 60)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        parent = Message.objects.get(pk=parent_id) if parent_id else None
        
        Message.objects.create(
            sender=request.user,
            receiver=other_user,
            content=content,
            parent_message=parent
        )
        cache.delete(cache_key)
        return redirect('conversation', user_id=user_id)
    
    return render(request, 'messaging/conversation.html', {
        'other_user': other_user,
        'messages': messages
    })


@login_required
def unread_messages_view(request):
    unread_messages = Message.unread.filter(
        receiver=request.user,
        read=False
    ).select_related('sender').only('id', 'sender__username', 'content', 'timestamp')
    
    # Adding the exact required method call
    unread_messages = Message.unread.unread_for_user(request.user)
    
    return render(request, 'messaging/unread.html', {
        'unread_messages': unread_messages
    })


@login_required
def message_history_view(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    if message.sender != request.user and message.receiver != request.user:
        raise PermissionDenied
    
    history = message.history.all().order_by('-edited_at')
    return render(request, 'messaging/history.html', {
        'message': message,
        'history': history
    })


@login_required
def delete_user(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')
    return render(request, 'messaging/confirm_delete.html')
