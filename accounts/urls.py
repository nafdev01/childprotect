# accounts/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "accounts"

urlpatterns = [
    # parent urls
    path("parent/login/", views.login_parent, name="login_parent"),
    path("parent/register/", views.register_parent, name="register_parent"),
    path("parent/dashboard/", views.parent_dashboard, name="parent_dashboard"),
    # child urls
    path("child/login/", views.login_child, name="login_child"),
    path("child/register/", views.register_child, name="register_child"),
    path("child/dashboard/", views.child_dashboard, name="child_dashboard"),
    # auth urls
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
