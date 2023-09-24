from django.contrib import admin
from .models import User, ParentProfile, ChildProfile, Confirmation


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "user_type")
    list_filter = ("user_type",)


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ("child", "parent_profile")
    list_filter = ("child", "parent_profile")


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("parent",)


@admin.register(Confirmation)
class ConfirmationAdmin(admin.ModelAdmin):
    list_display = ("user",)
