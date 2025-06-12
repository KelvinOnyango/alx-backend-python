from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created and not kwargs.get('raw', False):
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )


@receiver(pre_save, sender=Message)
def log_message_history(sender, instance, **kwargs):
    if instance.pk and not kwargs.get('raw', False):  # Only for updates
        try:
            old_message = sender.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                MessageHistory.objects.create(
                    message=instance,
                    content=old_message.content,
                    edited_by=instance.edited_by if instance.edited_by else instance.sender
                )
                instance.edited = True
        except sender.DoesNotExist:
            pass


@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    # All related data will be deleted through CASCADE
    pass
