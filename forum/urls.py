from django.urls import path
from forum import views

app_name = "forum"

urlpatterns = [
    # Display comments for a specific post
    path("", views.post_list, name="post_list"),
    # Create a comment for a specific post
    path("comment/<int:post_id>/", views.create_comment, name="create_og_comment"),
    path("reply/<int:comment_id>/", views.create_comment, name="create_reply"),
    path("add-subscriber/", views.add_subscriber, name="add_subscriber"),
    path("contact_message/", views.contact_message, name="contact_message"),
    path("chat/", views.chatPage, name="chat-page"),
]
