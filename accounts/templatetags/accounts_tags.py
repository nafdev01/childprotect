from django import template
from datetime import datetime, timedelta
from accounts.models import ChildProfile, ParentProfile, User
from safesearch.models import SearchPhrase, UnbanRequest
from django.utils import timezone

register = template.Library()


@register.simple_tag
def update_profile(parent):
    try:
        parent_profile = ParentProfile.objects.get(parent=parent)
        if (
            parent.first_name
            and parent.last_name
            and parent_profile.phone_number
            and parent_profile.address
            and parent_profile.gender
            and parent_profile.photo
        ):
            return False
        else:
            return True
    except ParentProfile.DoesNotExist:
        return 0


@register.inclusion_tag("accounts/includes/all_child_searches_modal.html")
def all_child_searches(childprofile_id):
    childprofile = ChildProfile.objects.get(id=childprofile_id)
    all_searches = SearchPhrase.objects.filter(searched_by=childprofile)
    return {
        "all_searches": all_searches,
        "username": childprofile.child.get_username(),
        "child_profile": childprofile,
    }


@register.inclusion_tag("accounts/includes/flagged_child_searches_modal.html")
def flagged_child_searches(childprofile_id):
    childprofile = ChildProfile.objects.get(id=childprofile_id)
    flagged_searches = SearchPhrase.flagged.filter(searched_by=childprofile)
    return {
        "flagged_searches": flagged_searches,
        "username": childprofile.child.get_username(),
        "child_profile": childprofile,
    }


@register.inclusion_tag("accounts/includes/child_unban_requests_modal.html")
def child_unban_requests(childprofile_id):
    childprofile = ChildProfile.objects.get(id=childprofile_id)
    unban_requests = UnbanRequest.objects.filter(requested_by=childprofile)
    return {
        "unban_requests": unban_requests,
        "username": childprofile.child.get_username(),
        "child_profile": childprofile,
    }


@register.simple_tag
def last_seven_dates(user, user_type):
    try:
        # Create a list to store the last 7 dates
        today = timezone.now().date()
        dates = [today]
        date_dict = dict()

        # Calculate the last 7 dates, including today
        for i in range(1, 7):
            previous_date = today - timedelta(days=i)
            dates.append(previous_date)

        dates.reverse()

        if user_type == "parent":
            parent_profile = ParentProfile.objects.get(parent=user)
            # Get today's date

            for date in dates:
                date_dict[f"{date.strftime('%A')}"] = SearchPhrase.objects.filter(
                    searched_by__parent_profile=parent_profile,
                    searched_on__date=date,
                ).count()
        elif user_type == "child":
            child_profile = ChildProfile.objects.get(child=user)
            # Get today's date

            for date in dates:
                date_dict[f"{date.strftime('%A')}"] = SearchPhrase.objects.filter(
                    searched_by=child_profile,
                    searched_on__date=date,
                ).count()

        return date_dict
    except ParentProfile.DoesNotExist:
        return 0
