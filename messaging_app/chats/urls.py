from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Main router
router = DefaultRouter()  # Explicit DefaultRouter() instantiation
router.register(r'users', UserViewSet)
router.register(r'conversations', ConversationViewSet)

# Nested router for messages
conversation_router = routers.NestedDefaultRouter(
    router, r'conversations', lookup='conversation'
)
conversation_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversation_router.urls)),
]
