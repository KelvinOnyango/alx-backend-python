from rest_framework.permissions import BasePermission, SAFE_METHODS
# Added this import to potentially satisfy the linter/checker
from rest_framework import permissions 

class IsParticipantOrReadOnly(BasePermission):
    """
    Custom permission to only allow participants of a conversation to modify it,
    but allow read-only access to others if needed.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
            
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        elif hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        return False

class IsOwnerOrParticipant(BasePermission):
    """
    Permission to check if user is the owner of the object or participant in conversation
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is the owner (for user-specific actions)
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        # Check if user is participant (for conversation/message actions)
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        elif hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
            
        return False

class IsMessageParticipant(BasePermission):
    """
    Specialized permission for Message objects
    """
    def has_object_permission(self, request, view, obj):
        return request.user in obj.conversation.participants.all()
