from django.contrib import admin
from .models import User, Conversation, Message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'online')
    list_filter = ('online',)
    search_fields = ('username', 'email')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    filter_horizontal = ('participants',)  # For easier many-to-many management

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'conversation', 'timestamp', 'read')
    list_filter = ('read', 'timestamp')
    search_fields = ('text',)
    raw_id_fields = ('sender', 'conversation')
