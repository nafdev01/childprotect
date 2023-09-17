from django.contrib import admin
from .models import SearchPhrase, BannedWord, FlaggedSearch, FlaggedWord


@admin.register(SearchPhrase)
class SearchPhraseAdmin(admin.ModelAdmin):
    list_display = ("phrase", "allowed")
    list_filter = ("allowed",)
    search_fields = ("phrase",)


@admin.register(BannedWord)
class BannedWordAdmin(admin.ModelAdmin):
    list_display = ("word", "reason", "date_added", "date_updated")
    list_filter = ("reason",)
    search_fields = ("word",)


@admin.register(FlaggedSearch)
class FlaggedSearchAdmin(admin.ModelAdmin):
    list_display = ("search_phrase", "flagged_on")
    list_filter = ("flagged_on",)
    search_fields = ("search_phrase__phrase",)


@admin.register(FlaggedWord)
class FlaggedWordAdmin(admin.ModelAdmin):
    list_display = ("flagged_word", "search_phrase", "flagged_on")
    list_filter = ("flagged_on",)
    search_fields = ("search_phrase__phrase", "flagged_word__word")
