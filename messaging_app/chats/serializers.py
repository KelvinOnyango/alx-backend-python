from rest_framework import serializers
from .models import User, Conversation, Message
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField(required=False, allow_null=True)
    online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'online'
        ]

    def get_online(self, obj):
        return obj.online

class MessageSerializer(serializers.ModelSerializer):
    message_id = serializers.CharField(read_only=True)
    message_body = serializers.CharField()
    sent_at = serializers.SerializerMethodField()
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'message_body', 'sent_at', 'read'
        ]

    def get_sent_at(self, obj):
        return obj.sent_at

    def validate_message_body(self, value):
        if len(value.strip()) == 0:
            raise ValidationError("Message body cannot be empty")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    conversation_id = serializers.CharField(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'messages',
            'created_at', 'updated_at'
        ]

    def get_created_at(self, obj):
        return obj.created_at

class ConversationCreateSerializer(serializers.ModelSerializer):
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
            raise ValidationError("A conversation must have at least 2 participants")
        return value

class MessageCreateSerializer(serializers.ModelSerializer):
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = ['message_body']

    def validate(self, data):
        if 'message_body' not in data or len(data['message_body'].strip()) == 0:
            raise ValidationError({"message_body": "Message body cannot be empty"})
        return data
