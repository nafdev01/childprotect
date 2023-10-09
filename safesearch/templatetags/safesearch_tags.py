from django import template
from accounts.models import *
from safesearch.models import *

register = template.Library()


@register.simple_tag
def get_alert_count(user):
    try:
        # Assuming your ParentProfile is related to User via a ForeignKey
        parent_profile = ParentProfile.objects.get(parent=user)
        alert_count = FlaggedAlert.objects.filter(
            flagged_search__search_phrase__searched_by__parent_profile_id=parent_profile.id,
            been_reviewed=False,
        ).count()
        return alert_count
    except ParentProfile.DoesNotExist:
        return 0


@register.simple_tag
def latest_alerts(parent):
    try:
        # Assuming your ParentProfile is related to User via a ForeignKey
        parent_profile = ParentProfile.objects.get(parent=parent)
        alerts = FlaggedAlert.objects.filter(
            flagged_search__search_phrase__searched_by__parent_profile_id=parent_profile.id,
            been_reviewed=False,
        )[:3]
        return alerts
    except ParentProfile.DoesNotExist:
        return 0


@register.simple_tag
def latest_unban_requests(parent):
    try:
        # Assuming your ParentProfile is related to User via a ForeignKey
        parent_profile = ParentProfile.objects.get(parent=parent)
        unban_requests = UnbanRequest.unreviewed.filter(
            requested_by__parent_profile=parent_profile
        )[:3]
        return unban_requests
    except ParentProfile.DoesNotExist:
        return 0
