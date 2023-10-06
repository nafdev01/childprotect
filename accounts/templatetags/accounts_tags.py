from django import template
from accounts.models import ParentProfile, User

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
