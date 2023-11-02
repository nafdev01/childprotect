from django.views.generic import TemplateView
from django.urls import path, include
from awareness import views

app_name = "awareness"

urlpatterns = [
    path("intro/", views.intro, name="intro"),
]
