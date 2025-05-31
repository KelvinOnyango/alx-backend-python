from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers  # Import for NestedDefaultRouter
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Main router using DefaultRouter
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('conversations', ConversationViewSet, basename='conversation')

# Nested router for messages under conversations
conversation_router = routers.NestedDefaultRouter(
    router, 'conversations', lookup='conversation'
)
conversation_router.register('messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversation_router.urls)),
]
