# consumers.py
import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.utils.text import slugify
from django.utils.timesince import timesince

from accounts.models import ChildProfile, ParentProfile, User
from safesearch.models import SiteVisit, ResultReport, SearchPhrase

channel_layer = get_channel_layer()

logger = logging.getLogger(__name__)


async def custom_save_result_report(text_data):
    try:
        text_data_json = json.loads(text_data)
        username = text_data_json["username"]
        parent_id = text_data_json["parent_id"]
        title = text_data_json["title"]
        link = text_data_json["link"]
        snippet = text_data_json["snippet"]
        reason = text_data_json["reason"]
        search_query_id = text_data_json["search_query_id"]
        search_phrase = await database_sync_to_async(SearchPhrase.objects.get)(
            id=search_query_id
        )
        child = await database_sync_to_async(User.children.get)(username=username)
        parent = await database_sync_to_async(User.parents.get)(id=parent_id)

        result_report = ResultReport(
            child=child,
            parent=parent,
            search=search_phrase,
            result_title=title,
            result_link=link,
            result_snippet=snippet,
            report_reason=reason,
        )

        await database_sync_to_async(result_report.save)()
        print(
            f"{result_report.child}'s  reported {result_report.result_title[:20]} to db"
        )
        return result_report
    except Exception as e:
        print(f"Error: {e}")
        logger.warning(f"Error: {e}")


async def custom_save_site_visit(text_data):
    try:
        text_data_json = json.loads(text_data)
        username = text_data_json["username"]
        parent_id = text_data_json["parent_id"]
        title = text_data_json["title"]
        link = text_data_json["link"]
        snippet = text_data_json["snippet"]
        search_query_id = text_data_json["search_query_id"]
        search_phrase = await database_sync_to_async(SearchPhrase.objects.get)(
            id=search_query_id
        )
        child = await database_sync_to_async(User.children.get)(username=username)
        parent = await database_sync_to_async(User.parents.get)(id=parent_id)
        site_visit = SiteVisit(
            child=child,
            parent=parent,
            search=search_phrase,
            site_title=title,
            site_link=link,
            site_snippet=snippet,
        )

        await database_sync_to_async(site_visit.save)()
        print(f"{site_visit.child} visited {site_visit.site_link}")
        return child.get_full_name(), site_visit
    except Exception as e:
        print(f"Error: {e}")
        logger.warning(f"Error: {e}")


class ResultReportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = "group_report_result"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_layer)

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


class SiteVisitConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["parent_id"]
        self.room_group_name = f"site_visit_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_layer)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        child, site_visit = await custom_save_site_visit(text_data)

        username = text_data_json["username"]
        title = text_data_json["title"]
        link = text_data_json["link"]
        snippet = text_data_json["snippet"]
        parent_id = text_data_json["parent_id"]

        success_response = {
            "type": "sendSiteVisit",
            "username": username,
            "title": title,
            "link": link,
            "snippet": snippet,
            "parent_id": parent_id,
            "full_name": child,
            "search_phrase": site_visit.search.phrase,
        }

        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                success_response,
            )
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")

    async def sendSiteVisit(self, event):
        try:
            username = event["username"]
            title = event["title"]
            link = event["link"]
            snippet = event["snippet"]
            search_phrase = event["search_phrase"]
            parent_id = event["parent_id"]
            full_name = event["full_name"]

            text_data = json.dumps(
                {
                    "username": username,
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "search_phrase": search_phrase,
                    "parent_id": parent_id,
                    "full_name": full_name,
                }
            )

            await self.send(text_data=text_data)
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")
