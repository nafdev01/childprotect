# consumers.py
import json
import logging
from urllib import request

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.utils.text import slugify
from django.utils.timesince import timesince
from django.utils import timezone

from accounts.models import ChildProfile, ParentProfile, User
from safesearch.models import (
    BannedWord,
    SiteVisit,
    ResultReport,
    SearchPhrase,
    UnbanRequest,
)
from safesearch.views import banned_word_list, unban_requests

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
        return child, parent, result_report
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


async def custom_unban_request(text_data):
    try:
        text_data_json = json.loads(text_data)
        word = text_data_json["word"]
        banned_word_id = text_data_json["banned_word_id"]
        unban_request_id = text_data_json["unban_request_id"]
        child_id = text_data_json["child_id"]
        parent_id = text_data_json["parent_id"]
        child = await database_sync_to_async(User.children.get)(id=child_id)
        child_profile = await database_sync_to_async(ChildProfile.objects.get)(
            child=child
        )
        banned_word = await database_sync_to_async(BannedWord.objects.get)(
            id=banned_word_id,
        )
        unban_request = await database_sync_to_async(UnbanRequest.objects.get)(
            id=unban_request_id
        )
        unban_request.been_reviewed = True
        unban_request.approved = True
        unban_request.reviewed_on = timezone.now()

        await database_sync_to_async(unban_request.save)()
        banned_word.is_banned = False

        await database_sync_to_async(banned_word.save)()
        print(f"You have unbanned the word {banned_word.word}")
        return child, banned_word
    except Exception as e:
        print(f"Error: {e}")
        logger.warning(f"Error: {e}")


async def custom_deny_unban_request(text_data):
    try:
        text_data_json = json.loads(text_data)
        banned_word_id = text_data_json["banned_word_id"]
        unban_request_id = text_data_json["unban_request_id"]
        child_id = text_data_json["child_id"]
        child = await database_sync_to_async(User.children.get)(id=child_id)
        banned_word = await database_sync_to_async(BannedWord.objects.get)(
            id=banned_word_id,
        )
        unban_request = await database_sync_to_async(UnbanRequest.objects.get)(
            id=unban_request_id
        )
        unban_request.been_reviewed = True
        unban_request.approved = False
        unban_request.reviewed_on = timezone.now()

        await database_sync_to_async(unban_request.save)()
        banned_word.is_banned = True

        await database_sync_to_async(banned_word.save)()
        print(f"You have denied an unban request for the word {banned_word.word}")
        return child, banned_word
    except Exception as e:
        print(f"Error: {e}")
        logger.warning(f"Error: {e}")


class ResultReportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["child_id"]
        self.room_group_name = f"report_result{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_layer)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        child, parent, result_report = await custom_save_result_report(text_data)

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
            "parent_id": parent.id,
            "full_name": child.get_full_name(),
            "search_phrase": result_report.search.phrase,
        }

        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                success_response,
            )
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
                    "full_name": event["full_name"],
                }
            )

            await self.send(text_data=text_data)
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")


class SiteVisitConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["child_id"]
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
        print(f"{self.room_group_name}")

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


class SearchAlertsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["child_id"]
        self.room_group_name = f"search_alerts_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_layer)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        username = text_data_json["username"]
        parent_id = text_data_json["parent_id"]

        child = await database_sync_to_async(User.children.get)(username=username)
        parent = await database_sync_to_async(User.parents.get)(id=parent_id)

    async def sendBannedAlert(self, event):
        try:
            title = event["title"]
            username = event["username"]
            text = event["text"]
            search_phrase = event["search_phrase"]

            text_data = json.dumps(
                {
                    "username": username,
                    "title": title,
                    "search_phrase": search_phrase,
                    "text": text,
                }
            )

            await self.send(text_data=text_data)
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")

    async def sendSuspiciousAlert(self, event):
        try:
            title = event["title"]
            username = event["username"]
            text = event["text"]
            search_phrase = event["search_phrase"]

            text_data = json.dumps(
                {
                    "username": username,
                    "title": title,
                    "search_phrase": search_phrase,
                    "text": text,
                }
            )
            await self.send(text_data=text_data)
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")


class UnbanRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["child_id"]
        self.room_group_name = f"unban_requests_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_layer)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            parent_id = text_data_json["parent_id"]
        except Exception as e:
            print(e)
            logger.warning(f"Error retrieving data: {e}")

        if text_data_json["type_of_request"] == "approve_request":
            child, banned_word = await custom_unban_request(text_data)

            success_response = {
                "type": "sendApprovedRequest",
                "title": f"You have approved an unban request for {child.get_full_name()}",
                "type_of_request": "approved_request",
                "word": banned_word.word,
                "child": f"{child.get_full_name()}",
            }

            try:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    success_response,
                )
            except Exception as e:
                print(e)
                logger.warning(f"Error: {e}")

        elif text_data_json["type_of_request"] == "deny_request":
            child, banned_word = await custom_deny_unban_request(text_data)

            success_response = {
                "type": "sendDeniedRequest",
                "title": f"You have denied an unban request for {child.get_full_name()}",
                "type_of_request": "denied_request",
                "word": banned_word.word,
                "child": f"{child.get_full_name()}",
            }

            try:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    success_response,
                )
            except Exception as e:
                print(e)
                logger.warning(f"Error: {e}")

    async def sendUnbanRequest(self, event):
        try:
            text_data = json.dumps(
                {
                    "title": event["title"],
                    "type_of_request": event["type_of_request"],
                    "word": event["word"],
                    "child": event["child"],
                    "banned_word_id": event["banned_word_id"],
                    "unban_request_id": event["unban_request_id"],
                }
            )

            await self.send(text_data=text_data)
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")

    async def sendApprovedRequest(self, event):
        try:
            text_data = json.dumps(
                {
                    "title": event["title"],
                    "type_of_request": event["type_of_request"],
                    "word": event["word"],
                    "child": event["child"],
                }
            )

            await self.send(text_data=text_data)
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")

    async def sendDeniedRequest(self, event):
        try:
            text_data = json.dumps(
                {
                    "title": event["title"],
                    "type_of_request": event["type_of_request"],
                    "word": event["word"],
                    "child": event["child"],
                }
            )

            await self.send(text_data=text_data)
        except Exception as e:
            print(e)
            logger.warning(f"Error: {e}")
