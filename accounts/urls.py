# accounts/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # parent urls
    path("", views.home, name="home"),
    path("login/", views.login_user, name="login"),
    path("parent/register/", views.register_parent, name="register_parent"),
    path("child/register/", views.register_child, name="register_child"),
    path("parent/profile/", views.parent_profile, name="parent_profile"),
    path("parent/children_details/", views.children_details, name="children_details"),
    path("update_parent_info/", views.update_parent_info, name="update_parent_info"),
    path(
        "update_parent_contacts/",
        views.update_parent_contacts,
        name="update_parent_contacts",
    ),
    path(
        "update_profile_photo/", views.update_profile_photo, name="update_profile_photo"
    ),
    # email confirmation urls
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    # child urls
    path("child/profile/", views.child_profile, name="child_profile"),
    path(
        "update_child_profile/", views.update_child_profile, name="update_child_profile"
    ),
    path(
        "update_child_info/<int:child_id>/",
        views.update_child_info,
        name="update_child_info",
    ),
    path(
        "update_child_password/<int:child_id>/",
        views.update_child_password,
        name="update_child_password",
    ),
    # auth urls
    path("logout/", views.logout_view, name="logout"),
    path(
        "parent/password_change/",
        views.parent_password_change,
        name="parent_password_change",
    ),
    path(
        "update_avatar/<int:child_id>",
        views.update_avatar,
        name="update_avatar",
    ),
]
