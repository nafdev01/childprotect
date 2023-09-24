# accounts/directors.py
from django.shortcuts import redirect
from .models import User, AccountStatus, UserType
from django.contrib import messages


def account_activation_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is logged in
        if request.user.is_authenticated:
            # Check if the user is a parent and their account is not activated
            if (
                request.user.user_type == UserType.PARENT
                and request.user.account_status == AccountStatus.NOTACTIVATED
            ):
                # Redirect the user to the view for not activated parents
                messages.error(
                    request, f"You must activate your account to access that page!"
                )
                return redirect("accounts:parent_not_activated")
        # If the user doesn't meet the conditions, proceed to the original view
        return view_func(request, *args, **kwargs)

    return _wrapped_view
