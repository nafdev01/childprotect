# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User
from forum.models import Post, Comment, TypeOfComment
from django.utils.text import slugify
from django.utils.timesince import timesince
from channels.layers import get_channel_layer
import logging

channel_layer = get_channel_layer()

logger = logging.getLogger(__name__)


async def custom_save_post(text_data):
    try:
        text_data_json = json.loads(text_data)
        username = text_data_json["username"]
        title = text_data_json["title"]
        content = text_data_json["content"]
        parent = await database_sync_to_async(User.objects.get)(username=username)
        post = Post(title=title, created_by=parent, content=content)
        await database_sync_to_async(post.save)()
        print(f"saved {post.title} by {post.created_by} to db")
        return post
    except Exception as e:
        print(f"Error: {e}")
        logger.warning(f"Error: {e}")


async def custom_save_og_comment(text_data):
    try:
        text_data_json = json.loads(text_data)
        username = text_data_json["username"]
        content = text_data_json["content"]
        post_id = text_data_json["post_id"]
        parent = await database_sync_to_async(User.objects.get)(username=username)
        post = await database_sync_to_async(Post.objects.get)(id=post_id)
        comment = Comment(
            comment_by=parent,
            post=post,
            content=content,
            type_of_comment=TypeOfComment.ORIGINAL,
        )
        await database_sync_to_async(comment.save)()
        print(f"saved {comment.comment_by}'s  og comment {comment.content[:20]} to db")
        return comment
    except Exception as e:
        print(f"Error: {e}")
        logger.warning(f"Error: {e}")


class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "group_post"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_layer)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        post = await custom_save_post(text_data)
        title = text_data_json["title"]
        username = text_data_json["username"]
        content = text_data_json["content"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "sendPost",
                "title": title,
                "username": username,
                "content": content,
                "url": post.get_absolute_url(),
            },
        )

    async def sendPost(self, event):
        title = event["title"]
        username = event["username"]
        content = event["content"]
        url = event["url"]
        text_data = json.dumps(
            {"title": title, "username": username, "content": content, "url": url}
        )

        await self.send(text_data=text_data)


class OgCommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["post_id"]
        self.room_group_name = f"post_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_layer)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        comment = await custom_save_og_comment(text_data)
        username = text_data_json["username"]
        content = text_data_json["content"]

        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "sendOgComment",
                    "username": username,
                    "content": content,
                    "comment_id": comment.id,
                    "comment_on": timesince(comment.comment_on),
                },
            )
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")

    async def sendOgComment(self, event):
        try:
            username = event["username"]
            content = event["content"]
            comment_id = event["comment_id"]
            comment_on = event["comment_on"]
            text_data = json.dumps(
                {
                    "username": username,
                    "content": content,
                    "comment_id": comment_id,
                    "comment_on": comment_on,
                }
            )

            await self.send(text_data=text_data)
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")
