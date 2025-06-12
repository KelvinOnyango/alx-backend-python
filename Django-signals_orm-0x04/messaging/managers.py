from django.db import models

class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        return self.filter(receiver=user, read=False).select_related('sender')
    
    def unread_for_user(self, user):
        return self.for_user(user).only('id', 'sender__username', 'content', 'timestamp')
