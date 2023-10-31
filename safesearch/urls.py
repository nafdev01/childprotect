from django.urls import path
from . import views

urlpatterns = [
    path("search/", views.search, name="search"),
    path(
        "search/history/",
        views.search_history,
        name="search_history",
    ),
    path(
        "search/history/<int:child_id>/",
        views.search_history,
        name="search_history_by_child",
    ),
    path(
        "banned_word/create/",
        views.create_banned_word,
        name="create_banned_word",
    ),
    path("banned_word/list/", views.banned_word_list, name="banned_words"),
    path(
        "banned_word/default_list/",
        views.default_banned_word_list,
        name="banned_words_default",
    ),
    path("banned_word/unban/<int:word_id>/", views.unban_word, name="unban_word"),
    path("banned_word/ban/<int:word_id>/", views.ban_word, name="ban_word"),
    path("alerts/", views.SearchAlertListView.as_view(), name="alert_list"),
    path("alerts/review/<int:alert_id>/", views.review_alert, name="review_alert"),
    path("add_banned_csv/", views.add_banned_csv, name="add_banned_csv"),
    path(
        "generate_pdf_report/<int:child_id>/",
        views.generate_pdf_report,
        name="generate_child_pdf_report",
    ),
    path(
        "generate_pdf_report/",
        views.generate_pdf_report,
        name="generate_children_pdf_report",
    ),
    path(
        "unban_request/create/<int:banned_word_id>/",
        views.create_unban_request,
        name="create_unban_request",
    ),
    path(
        "unban_requests/",
        views.UnbanRequestListView.as_view(),
        name="unban_requests",
    ),
    path(
        "unban_request/approve/<int:unban_request_id>/",
        views.approve_unban_request,
        name="approve_unban_request",
    ),
    path(
        "unban_request/deny/<int:unban_request_id>/",
        views.deny_unban_request,
        name="deny_unban_request",
    ),
]
