from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated # Keep this if needed for global default
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
# Import your custom permission
from .permissions import IsParticipantOfConversation # This is the new import

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
    # Apply the custom permission. IsAuthenticated will be handled by the global default.
    permission_classes = [IsParticipantOfConversation] 
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
        # Ensure only conversations the user is a participant of are retrieved
        # This complements the object-level permission for safety.
        return self.queryset.filter(participants=self.request.user).distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Ensure that the creating user is automatically added as a participant
        # before saving the conversation.
        participants_data = request.data.get('participants', [])
        if request.user.id not in participants_data:
            participants_data.append(request.user.id)
        request.data['participants'] = participants_data

        self.perform_create(serializer)
        conversation = serializer.instance
        # The line below might be redundant if participant is already added in serializer's create/save
        # conversation.participants.add(request.user) 
        headers = self.get_success_headers(serializer.data)
        return Response(
            ConversationSerializer(conversation, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class MessageViewSet(viewsets.ModelViewSet):
    # Apply the custom permission. IsAuthenticated will be handled by the global default.
    permission_classes = [IsParticipantOfConversation]
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
        # Ensure only messages from conversations the user is a participant of are retrieved
        # This complements the object-level permission for safety.
        return self.queryset.filter(conversation__participants=self.request.user).distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation_id = request.data.get('conversation')
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            
            # Use the permission class for checking access
            # The IsParticipantOfConversation will handle this check, 
            # so this explicit check might be removed depending on strictness.
            # However, keeping it provides an early exit for clarity.
            if request.user not in conversation.participants.all():
                raise PermissionDenied("You are not a participant in this conversation.")
            
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
