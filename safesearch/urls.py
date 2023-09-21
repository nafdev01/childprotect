from django.urls import path
from . import views

app_name = "safesearch"

urlpatterns = [
    path("search/", views.search, name="search"),
    path("search/history/", views.child_search_history, name="child_search_history"),
    path(
        "search/child/history/",
        views.parent_search_history,
        name="parent_search_history",
    ),
    path("banned_word/create/", views.create_banned_word, name="create_banned_word"),
    path("banned_word/list/", views.banned_word_list, name="banned_words"),
    path("alerts/", views.alert_list, name="alert_list"),
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
]
