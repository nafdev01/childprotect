from django.shortcuts import render
from rest_framework import viewsets

from safesearch.models import (
    BannedDefault,
    BannedWord,
    SearchAlert,
    SearchPhrase,
    SiteVisit,
    UnbanRequest,
)

from .serializers import (
    BannedDefaultSerializer,
    BannedWordSerializer,
    SearchAlertSerializer,
    SearchPhraseSerializer,
    SiteVisitSerializer,
    UnbanRequestSerializer,
)


# Create your views here.
class BannedWordViewSet(viewsets.ModelViewSet):
    queryset = BannedWord.objects.all()
    serializer_class = BannedWordSerializer


class BannedDefaultViewSet(viewsets.ModelViewSet):
    queryset = BannedDefault.objects.all()
    serializer_class = BannedDefaultSerializer


class SearchAlertViewSet(viewsets.ModelViewSet):
    queryset = SearchAlert.objects.all()
    serializer_class = SearchAlertSerializer


class SearchPhraseViewSet(viewsets.ModelViewSet):
    queryset = SearchPhrase.objects.all()
    serializer_class = SearchPhraseSerializer


class SiteVisitViewSet(viewsets.ModelViewSet):
    queryset = SiteVisit.objects.all()
    serializer_class = SiteVisitSerializer


class UnbanRequestViewSet(viewsets.ModelViewSet):
    queryset = UnbanRequest.objects.all()
    serializer_class = UnbanRequestSerializer
