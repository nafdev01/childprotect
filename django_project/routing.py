from django.urls import path
from forum.consumers import PostConsumer, OgCommentConsumer
from safesearch.consumers import ResultReportConsumer, SiteVisitConsumer
from django.urls import re_path

websocket_urlpatterns = [
    path("ws/", PostConsumer.as_asgi()),
    re_path(r"ws/og/comment/(?P<post_id>\w+)/$", OgCommentConsumer.as_asgi()),
    path("ws/report/result/", ResultReportConsumer.as_asgi()),
    re_path(r"ws/site/visit/(?P<parent_id>\w+)/$", SiteVisitConsumer.as_asgi()),
]
