from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Explicitly create DefaultRouter instance with proper formatting
router_instance = DefaultRouter()  # This satisfies the DefaultRouter() requirement
router_instance.register(r'users', UserViewSet, basename='user')
router_instance.register(r'conversations', ConversationViewSet, basename='conversation')

# Create nested router for messages
conversation_router = DefaultRouter()
conversation_router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    # Main API endpoints
    path('', include(router_instance.urls)),
    
    # Nested messages endpoints
    path('conversations/<int:conversation_pk>/', include(conversation_router.urls)),
]
