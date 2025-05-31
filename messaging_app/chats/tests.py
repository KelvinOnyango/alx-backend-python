from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertFalse(self.user.online)

class ConversationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1')
        self.user2 = User.objects.create_user(username='user2')
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_conversation_creation(self):
        self.assertEqual(self.conversation.participants.count(), 2)
        self.assertTrue(self.user1 in self.conversation.participants.all())
        self.assertTrue(self.user2 in self.conversation.participants.all())

class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='sender')
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user)
        self.message = Message.objects.create(
            sender=self.user,
            conversation=self.conversation,
            text='Test message'
        )

    def test_message_creation(self):
        self.assertEqual(self.message.text, 'Test message')
        self.assertFalse(self.message.read)
        self.assertEqual(self.message.sender, self.user)
        self.assertEqual(self.message.conversation, self.conversation)
