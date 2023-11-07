from django.urls import path, re_path

from forum.consumers import OgCommentConsumer, PostConsumer
from safesearch.consumers import (SearchAlertsConsumer, ResultReportConsumer,
                                  SiteVisitConsumer,UnbanRequestConsumer)

websocket_urlpatterns = [
    path("ws/", PostConsumer.as_asgi()),
    re_path(r"ws/og/comment/(?P<post_id>\w+)/$", OgCommentConsumer.as_asgi()),
    re_path(r"ws/report/result/(?P<child_id>\w+)/$", ResultReportConsumer.as_asgi()),
    re_path(r"ws/site/visit/(?P<child_id>\w+)/$", SiteVisitConsumer.as_asgi()),
    re_path(r"ws/search/alerts/(?P<child_id>\w+)/$", SearchAlertsConsumer.as_asgi()),
    re_path(r"ws/unban/requests/(?P<child_id>\w+)/$", UnbanRequestConsumer.as_asgi()),
]
