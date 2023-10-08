from django.contrib import admin
from .models import FlaggedAlert, SearchPhrase, BannedWord, FlaggedSearch, FlaggedWord


@admin.register(SearchPhrase)
class SearchPhraseAdmin(admin.ModelAdmin):
    list_display = ("phrase", "allowed")
    list_filter = ("allowed",)


@admin.register(BannedWord)
class BannedWordAdmin(admin.ModelAdmin):
    list_display = ("word", "reason", "date_added", "date_updated")
    list_filter = ("reason",)
    search_fields = ["word"]


@admin.register(FlaggedSearch)
class FlaggedSearchAdmin(admin.ModelAdmin):
    list_display = ("search_phrase", "flagged_on")
    list_filter = ("flagged_on",)


@admin.register(FlaggedWord)
class FlaggedWordAdmin(admin.ModelAdmin):
    list_display = ("flagged_word", "flagged_search", "flagged_on")
    list_filter = ("flagged_on",)


@admin.action(description="Mark alerts as unreviewed")
def make_unreviewed(modeladmin, request, queryset):
    queryset.update(been_reviewed=False)


@admin.register(FlaggedAlert)
class FlaggedAlertAdmin(admin.ModelAdmin):
    list_display = ("flagged_search", "been_reviewed", "reviewed_on")
    list_filter = ("been_reviewed",)
    actions = [make_unreviewed]
