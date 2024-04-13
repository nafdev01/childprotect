from rest_framework import serializers

from safesearch.models import (
    BannedDefault,
    BannedWord,
    SearchAlert,
    SearchPhrase,
    SearchStatus,
    SiteVisit,
    UnbanRequest,
)


class BannedWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannedWord
        fields = "__all__"


class BannedDefaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannedDefault
        fields = "__all__"


class SearchAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchAlert
        fields = "__all__"


class SearchPhraseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchPhrase
        fields = "__all__"

class SiteVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteVisit
        fields = "__all__"


class UnbanRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnbanRequest
        fields = "__all__"
