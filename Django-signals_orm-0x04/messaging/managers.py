from django.db import models

class UnreadMessagesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(read=False)
    
    def for_user(self, user):
        return self.filter(receiver=user).select_related('sender')
    
    def unread_for_user(self, user):
        return self.for_user(user).only('id', 'sender__username', 'content', 'timestamp')
