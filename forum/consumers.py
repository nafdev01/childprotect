# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User
from forum.models import Post


async def custom_save_post(text_data):
    try:
        text_data_json = json.loads(text_data)
        username = text_data_json["username"]
        title = text_data_json["title"]
        content = text_data_json["content"]
        username = await database_sync_to_async(User.objects.get)(username=username)
        post = Post(title=title, created_by=username, content=content)
        await database_sync_to_async(post.save)()
        print(f"saved {post.title} by {post.created_by} to db")
    except Exception as e:
        print(f"Error: {e}")


class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.roomGroupName = "grouppost"
        await self.channel_layer.group_add(self.roomGroupName, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.roomGroupName, self.channel_layer)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        await custom_save_post(text_data)
        title = text_data_json["title"]
        username = text_data_json["username"]
        content = text_data_json["content"]

        await self.channel_layer.group_send(
            self.roomGroupName,
            {
                "type": "sendPost",
                "title": title,
                "username": username,
                "content": content,
            },
        )

    async def sendPost(self, event):
        title = event["title"]
        username = event["username"]
        content = event["content"]
        text_data = json.dumps(
            {"title": title, "username": username, "content": content}
        )

        await self.send(text_data=text_data)
