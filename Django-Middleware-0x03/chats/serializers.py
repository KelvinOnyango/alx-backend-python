from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model with enhanced fields"""
    user_id = serializers.CharField(read_only=True)
    username = serializers.CharField()
    email = serializers.CharField()
    full_name = serializers.SerializerMethodField()
    online_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "online",
            "full_name",
            "online_status"
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_online_status(self, obj):
        return "Online" if obj.online else "Offline"

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model with validation"""
    message_id = serializers.CharField(read_only=True)
    message_body = serializers.CharField()
    sender = UserSerializer(read_only=True)
    sent_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Message
        fields = [
            "message_id",
            "sender",
            "conversation",
            "message_body",
            "sent_at",
            "read"
        ]
        read_only_fields = ["message_id", "sent_at", "sender"]

    def validate_message_body(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        if len(value.strip()) > 1000:
            raise serializers.ValidationError("Message too long (max 1000 chars)")
        return value.strip()

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested relationships"""
    conversation_id = serializers.CharField(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "created_at",
            "updated_at",
            "messages",
            "last_message"
        ]

    def get_messages(self, obj):
        messages = obj.messages.order_by('-sent_at')[:20]  # Get last 20 messages
        return MessageSerializer(messages, many=True, context=self.context).data

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return MessageSerializer(last_message, context=self.context).data
        return None

class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating conversations"""
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=True
    )

    class Meta:
        model = Conversation
        fields = ['participants']

    def validate_participants(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Need at least 2 participants")
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 participants allowed")
        return value
