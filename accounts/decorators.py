from django.shortcuts import redirect
from django.contrib import messages


def parent_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_parent:
                # User is authenticated and is a parent, allow access to the view.
                return view_func(request, *args, **kwargs)
            else:
                # User is authenticated but is a child, redirect to the child dashboard view.
                messages.error(
                    request,
                    "Only parents are allowed to access this page. If you are a parent, please log in with your parent account.",
                )
                return redirect(
                    "accounts:child_dashboard"
                )  # Replace with the actual URL name of the child dashboard view.
        else:
            # User is not authenticated, redirect to the login view.
            messages.error(
                request,
                "You need to log in as a parent to access this page. If you do not have a parent account, please sign up.",
            )
            return redirect(
                "accounts:login"
            )  # Replace with the actual URL name of the login view.

    return wrapper


def child_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_parent:
                # User is authenticated and is a child, allow access to the view.
                return view_func(request, *args, **kwargs)
            else:
                # User is authenticated but is a parent, redirect to the parent dashboard view.
                messages.error(
                    request,
                    "Only children are allowed to access this page. If you are a child, please log in with your child account.",
                )
                return redirect(
                    "accounts:parent_dashboard"
                )  # Replace with the actual URL name of the parent dashboard view.
        else:
            # User is not authenticated, redirect to the login view.
            messages.error(
                request,
                "You need to log in as a child to access this page. If you don't have a child account, please request your parent sign you up.",
            )
            return redirect(
                "accounts:login"
            )  # Replace with the actual URL name of the login view.

    return wrapper


def guest_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # User is not authenticated (guest user), allow access to the view.
            return view_func(request, *args, **kwargs)
        elif request.user.is_parent:
            # User is authenticated and is a parent, redirect to the parent dashboard view.
            messages.error(
                request,
                "You are already logged in as a parent. If you want to access the guest page, please log out first.",
            )
            return redirect(
                "accounts:parent_dashboard"
            )  # Replace with the actual URL name of the parent dashboard view.
        else:
            # User is authenticated but is a child, redirect to the child dashboard view.
            messages.error(
                request,
                "You are already logged in as a child. If you want to access the guest page, please log out first.",
            )
            return redirect(
                "accounts:child_dashboard"
            )  # Replace with the actual URL name of the child dashboard view.

    return wrapper
