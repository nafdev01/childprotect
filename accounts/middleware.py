# middleware.py
from django.utils import timezone


class ChildLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_child:
            # Update the last seen time for child profiles
            child_profile = request.user.childprofile
            child_profile.last_seen = timezone.now()
            child_profile.save()

        response = self.get_response(request)
        return response
