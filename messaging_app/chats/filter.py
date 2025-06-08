import django_filters
from .models import Message, Conversation, User

class MessageFilter(django_filters.FilterSet):
    """
    FilterSet for Message objects.
    Allows filtering messages by:
    - sent_at__gte (messages sent on or after a specific date/time)
    - sent_at__lte (messages sent on or before a specific date/time)
    - sender (messages sent by a specific user ID)
    - conversation__participants (messages in conversations involving specific user IDs)
    """
    # Filter for messages sent after or on a specific date/time
    sent_at_after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    
    # Filter for messages sent before or on a specific date/time
    sent_at_before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    
    # Filter for messages sent by a specific user (by user ID)
    # This assumes 'sender' is a ForeignKey to your User model
    sender = django_filters.NumberFilter(field_name='sender__id')

    # Filter for messages within conversations involving specific participants
    # This allows you to find messages in conversations where a given user is a participant.
    # You can provide multiple participant IDs separated by commas for an OR condition.
    # e.g., ?conversation_participants=1,2 will show messages from conversations
    # where user 1 OR user 2 is a participant.
    conversation_participants = django_filters.ModelMultipleChoiceFilter(
        field_name='conversation__participants',
        to_field_name='id', # Assumes 'id' is the primary key of your User model
        queryset=User.objects.all(),
        conjoined=False # False means it's an OR condition for multiple choices
    )

    class Meta:
        model = Message
        fields = [
            'sent_at',          # Exact match for sent_at (less common for datetime)
            'sent_at_after',    # Custom filter for >= date/time
            'sent_at_before',   # Custom filter for <= date/time
            'sender',           # Filter by sender ID (will use sender__id implicitly here if just 'sender' is used)
            'conversation',     # Filter by exact conversation ID
            'read',             # Filter by read status (True/False)
            'conversation_participants', # Custom filter for conversation participants
        ]
