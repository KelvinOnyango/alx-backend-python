from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from chats.auth import CustomTokenObtainPairView
from chats.views import UserViewSet, ConversationViewSet, MessageViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

# Main API router
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('conversations', ConversationViewSet, basename='conversation')

# Nested router for messages under conversations
conversation_router = routers.NestedDefaultRouter(
    router, 'conversations', lookup='conversation'
)
conversation_router.register('messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/', include(conversation_router.urls)),
    
    # DRF auth (for browsable API)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
