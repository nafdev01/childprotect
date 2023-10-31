from django.urls import path
from forum.consumers import PostConsumer

# Here, "" is routing to the URL ChatConsumer which
# will handle the chat functionality.
websocket_urlpatterns = [
    path("ws/", PostConsumer.as_asgi()),
]
