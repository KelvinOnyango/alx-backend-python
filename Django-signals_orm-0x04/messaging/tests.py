from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()


class MessagingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')

    def test_message_creation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Hello there'
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, 'Hello there')
        self.assertFalse(message.read)
        self.assertFalse(message.edited)

    def test_notification_created(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Hello there'
        )
        notification = Notification.objects.get(message=message)
        self.assertEqual(notification.user, self.user2)
        self.assertFalse(notification.read)

    def test_message_edit_history(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Hello there'
        )
        message.content = 'Hello there! Edited'
        message.save()
        self.assertTrue(message.edited)
        history = MessageHistory.objects.get(message=message)
        self.assertEqual(history.content, 'Hello there')

    def test_unread_manager(self):
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Message 1'
        )
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Message 2',
            read=True
        )
        unread = Message.unread.for_user(self.user2)
        self.assertEqual(unread.count(), 1)
        self.assertEqual(unread.first().content, 'Message 1')

    def test_threaded_messages(self):
        parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Parent message'
        )
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Reply message',
            parent_message=parent
        )
        self.assertEqual(parent.replies.count(), 1)
        self.assertEqual(parent.replies.first(), reply)

    def test_user_deletion(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test message'
        )
        notification = Notification.objects.get(message=message)
        self.user1.delete()
        # Check if related data was deleted (through CASCADE)
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(pk=message.pk)
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(pk=notification.pk)
