from django.urls import path
from forum.consumers import PostConsumer, OgCommentConsumer
from safesearch.consumers import ResultReportConsumer, SiteVisitConsumer
from django.urls import re_path

websocket_urlpatterns = [
    path("ws/", PostConsumer.as_asgi()),
    re_path(r"ws/og/comment/(?P<post_id>\w+)/$", OgCommentConsumer.as_asgi()),
    re_path(r"ws/report/result/(?P<child_id>\w+)/$", ResultReportConsumer.as_asgi()),
    re_path(r"ws/site/visit/(?P<child_id>\w+)/$", SiteVisitConsumer.as_asgi()),
]
