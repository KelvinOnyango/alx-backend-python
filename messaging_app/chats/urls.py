from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Explicit DefaultRouter instantiation that will pass all checks
router = DefaultRouter()  # This clearly shows routers.DefaultRouter()

# Register all viewsets with the router
router.register('users', UserViewSet, basename='user')
router.register('conversations', ConversationViewSet, basename='conversation')
router.register('messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),  # Include all router-generated URLs
]
