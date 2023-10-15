from django.contrib import admin
from forum.models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "posted_on")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post",  "reply_to")
