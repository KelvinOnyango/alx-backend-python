from rest_framework import serializers
from .models import CustomUser, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the CustomUser model, excluding password and sensitive fields."""

    full_name = serializers.SerializerMethodField()
    username = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = [
            "user_id",
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "profile_picture",
            "phone_number",
            "is_online",
            "last_seen",
            "full_name",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model, including sender and conversation details."""

    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = ["message_id", "sender", "conversation", "message_body", "sent_at"]
        read_only_fields = ["message_id", "sent_at"]

    def validate_message_body(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Message body cannot be empty.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for the Conversation model, including participants and messages."""

    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True, source="messages")

    class Meta:
        model = Conversation
        fields = ["conversation_id", "participants", "created_at", "messages"]
