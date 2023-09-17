from django.contrib import admin
from .models import User, ParentProfile, ChildProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "user_type")
    list_filter = ("user_type",)


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ("child", "account_status")
    list_filter = ("account_status",)


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("parent",)
