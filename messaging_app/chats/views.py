from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    MessageSerializer,
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageCreateSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['online']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'last_seen']
    ordering = ['username']

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Conversation.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['participants']
    ordering_fields = ['updated_at']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer

    def get_queryset(self):
        return self.queryset.filter(participants=self.request.user)

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['conversation', 'sender', 'read']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        return self.queryset.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        conversation_id = self.request.data.get('conversation')
        conversation = Conversation.objects.get(id=conversation_id)
        if self.request.user in conversation.participants.all():
            serializer.save(sender=self.request.user, conversation=conversation)
        else:
            raise PermissionDenied("You are not a participant in this conversation")
