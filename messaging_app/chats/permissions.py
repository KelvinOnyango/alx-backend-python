from rest_framework.permissions import BasePermission, SAFE_METHODS
# This import is generally not strictly needed if you only use BasePermission and SAFE_METHODS
# from rest_framework import permissions 

class IsParticipantOfConversation(BasePermission):
    """
    Custom permission to allow only authenticated users who are participants
    in a conversation to perform actions on messages within that conversation.
    """

    def has_permission(self, request, view):
        # Allow only authenticated users to access the API at a general level
        # This is implicitly handled by DEFAULT_PERMISSION_CLASSES in settings.py
        # but added here for explicit clarity in this permission class's role.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow read-only access (GET, HEAD, OPTIONS) for any authenticated user
        # This part might be adjusted based on exact requirements.
        # If only participants should even VIEW, remove this and rely on the below.
        if request.method in SAFE_METHODS:
            # For GET/HEAD/OPTIONS, allow if user is authenticated and is a participant
            # This ensures even viewing requires participation.
            if isinstance(obj, Conversation):
                return request.user in obj.participants.all()
            elif hasattr(obj, 'conversation'): # For Message objects
                return request.user in obj.conversation.participants.all()
            return False # Default deny if object type is unexpected

        # For write operations (POST, PUT, PATCH, DELETE)
        # Check if the user is a participant in the conversation
        if isinstance(obj, Conversation):
            # For Conversation objects, check if the user is a participant
            return request.user in obj.participants.all()
        elif hasattr(obj, 'conversation'):
            # For Message objects, check if the user is a participant of the associated conversation
            return request.user in obj.conversation.participants.all()
        
        return False # Default deny for other object types


# The previous permission classes are not explicitly part of the prompt's
# requirement for this task, but I'll keep them commented out if you might
# want to use them for other purposes later.
# class IsOwnerOrParticipant(BasePermission):
#     """
#     Permission to check if user is the owner of the object or participant in conversation
#     """
#     def has_object_permission(self, request, view, obj):
#         # Check if user is the owner (for user-specific actions)
#         if hasattr(obj, 'user'):
#             return obj.user == request.user
            
#         # Check if user is participant (for conversation/message actions)
#         if hasattr(obj, 'participants'):
#             return request.user in obj.participants.all()
#         elif hasattr(obj, 'conversation'):
#             return request.user in obj.conversation.participants.all()
            
#         return False

# class IsMessageParticipant(BasePermission):
#     """
#     Specialized permission for Message objects
#     """
#     def has_object_permission(self, request, view, obj):
#         return request.user in obj.conversation.participants.all()
