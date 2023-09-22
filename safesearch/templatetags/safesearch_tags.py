from django import template
from accounts.models import ParentProfile
from safesearch.models import FlaggedAlert

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