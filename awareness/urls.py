from django.views.generic import TemplateView
from django.urls import path, include
from awareness import views

app_name = "awareness"

urlpatterns = [
    path("intro/", views.intro, name="intro"),
    path("bahati/", views.bahati, name="bahati"),
    path("klein/", views.klein, name="klein"),
    path("meki/", views.meki, name="meki"),
]
