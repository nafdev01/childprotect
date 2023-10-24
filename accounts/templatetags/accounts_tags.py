from django import template
from accounts.models import ChildProfile, ParentProfile, User
from safesearch.models import SearchPhrase, FlaggedSearch, UnbanRequest


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
        "profile": childprofile,
    }


@register.inclusion_tag("accounts/includes/flagged_child_searches_modal.html")
def flagged_child_searches(childprofile_id):
    childprofile = ChildProfile.objects.get(id=childprofile_id)
    flagged_searches = FlaggedSearch.objects.filter(searched_by=childprofile)
    return {
        "flagged_searches": flagged_searches,
        "username": childprofile.child.get_username(),
        "profile": childprofile,
    }


@register.inclusion_tag("accounts/includes/child_unban_requests_modal.html")
def child_unban_requests(childprofile_id):
    childprofile = ChildProfile.objects.get(id=childprofile_id)
    unban_requests = UnbanRequest.objects.filter(requested_by=childprofile)
    return {
        "unban_requests": unban_requests,
        "username": childprofile.child.get_username(),
        "profile": childprofile,
    }
