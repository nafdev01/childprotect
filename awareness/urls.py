from django.views.generic import TemplateView
from django.urls import path, include

app_name = "awareness"

urlpatterns = [
    path("intro/", TemplateView.as_view(template_name="intro.html"), name="intro"),
]
