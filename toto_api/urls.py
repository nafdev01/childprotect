from django.urls import path
from toto_api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("bannedword", views.BannedWordViewSet)
router.register("banneddefault", views.BannedDefaultViewSet)
router.register("searchalert", views.SearchAlertViewSet)
router.register("searchphrase", views.SearchPhraseViewSet)
router.register("sitevisit", views.SiteVisitViewSet)
router.register("unbanrequest", views.UnbanRequestViewSet)


urlpatterns = []


urlpatterns += router.urls
