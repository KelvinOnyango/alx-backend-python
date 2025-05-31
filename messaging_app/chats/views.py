from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        conversation = serializer.instance
        conversation.participants.add(request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            ConversationSerializer(conversation, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation_id = request.data.get('conversation')
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response(
                    {"detail": "You are not a participant in this conversation"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            message = serializer.save(sender=request.user, conversation=conversation)
            headers = self.get_success_headers(serializer.data)
            return Response(
                MessageSerializer(message, context=self.get_serializer_context()).data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND
            )
