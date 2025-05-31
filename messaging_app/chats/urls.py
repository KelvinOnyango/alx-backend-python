from django.urls import path, include
from rest_framework_nested import routers
from .views import ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")

nested_router = routers.NestedDefaultRouter(
    router, r"conversations", lookup="conversation"
)
nested_router.register(r"messages", MessageViewSet, basename="conversation-messages")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(nested_router.urls)),
]
