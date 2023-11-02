# django_project/urls.py
from django.views.generic import TemplateView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("about", TemplateView.as_view(template_name="about.html"), name="about"),
    path("contact", TemplateView.as_view(template_name="contact.html"), name="contact"),
    path("", include("accounts.urls")),
    path("forum/", include("forum.urls")),
    path("", include("safesearch.urls")),
    path("awareness/", include("awareness.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

handler404 = 'accounts.views.custom_404'
