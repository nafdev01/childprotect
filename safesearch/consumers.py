# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User, ChildProfile, ParentProfile
from safesearch.models import SearchPhrase
from django.utils.text import slugify
from django.utils.timesince import timesince
from safesearch.models import ResultReport
from channels.layers import get_channel_layer
import logging

channel_layer = get_channel_layer()

logger = logging.getLogger(__name__)


async def custom_save_result_report(text_data):
    try:
        text_data_json = json.loads(text_data)
        username = text_data_json["username"]
        title = text_data_json["title"]
        link = text_data_json["link"]
        snippet = text_data_json["snippet"]
        reason = text_data_json["reason"]
        search_query_id = text_data_json["search_query_id"]
        search_phrase = await database_sync_to_async(SearchPhrase.objects.get)(
            id=search_query_id
        )
        child = await database_sync_to_async(User.objects.get)(username=username)
        result_report = ResultReport(
            child=child,
            search=search_phrase,
            result_title=title,
            result_link=link,
            result_snippet=snippet,
            report_reason=reason,
        )

        await database_sync_to_async(result_report.save)()
        print(
            f"saved {result_report.child}'s  reported {result_report.result_title[:20]} to db"
        )
        return result_report
    except Exception as e:
        print(f"Error: {e}")
        logger.warning(f"Error: {e}")



class ResultReportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.roomGroupName = "group_report_result"
        await self.channel_layer.group_add(self.roomGroupName, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.roomGroupName, self.channel_layer)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        report_result = await custom_save_result_report(text_data)

        username = text_data_json["username"]
        title = text_data_json["title"]
        link = text_data_json["link"]
        snippet = text_data_json["snippet"]
        reason = text_data_json["reason"]

        success_response = {
            "type": "sendParentReport",
            "username": username,
            "title": title,
            "link": link,
            "snippet": snippet,
            "reason": reason,
            "search_phrase": report_result.search.phrase,
        }

        try:
            await self.send(text_data=json.dumps(success_response))
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")


    async def sendParentReport(self, event):
        try:
            username = event["username"]
            title = event["title"]
            link = event["link"]
            snippet = event["snippet"]
            reason = event["reason"]
            search_phrase = event["search_phrase"]

            text_data = json.dumps(
                {
                    "username": username,
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "reason": reason,
                    "search_phrase": search_phrase,
                }
            )

            await self.send(text_data=text_data)
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")

