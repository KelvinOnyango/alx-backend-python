from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ConversationViewSet, MessageViewSet


router = DefaultRouter() # routers.DefaultRouter()


router.register('users', UserViewSet, basename='user')
router.register('conversations', ConversationViewSet, basename='conversation')
router.register('messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)), 
]
