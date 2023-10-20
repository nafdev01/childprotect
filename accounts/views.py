from django.shortcuts import render, redirect
from django.urls import reverse
from accounts.decorators import parent_required, child_required, guest_required
from .forms import *
from .notifications import *
from .models import User, ParentProfile, ChildProfile, AccountStatus
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import Confirmation
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm


# logout view
def logout_view(request):
    messages.success(request, "You have logged out successfully!")
    logout(request)
    return redirect("accounts:login")


# login view
@guest_required
def login_user(request):
    if request.method == "POST":
        # Retrieve username and password from POST data
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type")

        if not (username and password and user_type):
            messages.error(f"Fill in the form fields as required")
        elif username and password and user_type:
            try:
                if user_type == "parent":
                    parent = User.parents.get(username=username)

                    if not parent.is_active:
                        messages.error(
                            request,
                            f"Please confirm your email at {parent.email[:5]}**************{parent.email[-5:]} before attempting to log in",
                        )
                        return redirect(reverse("accounts:login"))
                    else:
                        parent = authenticate(
                            request,
                            username=username,
                            password=password,
                        )

                        if (
                            parent is not None
                            and parent.user_type == User.UserType.PARENT
                        ):
                            login(request, parent)
                            # send_parent_login_email(request)
                            messages.success(request, "Parent Log In Successful!")
                            # send_parent_login_email(request)
                            return redirect("accounts:parent_dashboard")
                        else:
                            messages.error(
                                request, "Invalid parent username or password."
                            )

                elif user_type == "child":
                    child = User.children.get(username=username)

                    if not child.is_active:
                        messages.error(
                            request,
                            f"Your account is inactive",
                        )
                        return redirect(reverse("accounts:login"))
                    else:
                        child = authenticate(
                            request,
                            username=username,
                            password=password,
                        )

                        if child is not None and child.user_type == User.UserType.CHILD:
                            login(request, child)
                            messages.success(request, "Child Log In Successful!")
                            send_child_login_email(request)
                            return redirect("accounts:child_dashboard")
                        else:
                            messages.error(
                                request, "Invalid child username or password."
                            )

            except User.DoesNotExist:
                messages.error(request, "Invalid username or password.")

    template_name = "registration/login.html"
    return render(request, template_name)


# View for parent user registration with profile information
@guest_required
def register_parent(request):
    if request.method == "POST":
        parent_form = ParentRegistrationForm(request.POST)

        if parent_form.is_valid():
            parent = parent_form.save(commit=False)
            parent.user_type = User.UserType.PARENT
            parent.is_active = False
            parent.save()
            parent_profile = ParentProfile.create(parent=parent)
            parent_profile.save()

            # Create a confirmation token
            token = token_generator.make_token(parent)
            Confirmation.objects.create(user=parent, token=token)
            current_site = get_current_site(request)
            token_dict = {
                "protocol": request.scheme,
                "parent": parent,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(parent.pk)),
                "token": token,
            }

            messages.success(
                request,
                "Your account has been created successfully! Please check your email to confirm your email address and activate your account.",
            )
            send_parent_signup_confirm_email(request, parent, token_dict)
            return redirect("accounts:login")

    else:
        parent_form = ParentRegistrationForm()

    template_name = "registration/parent_registration.html"
    context = {"parent_form": parent_form}
    return render(request, template_name, context)


# activate parent account after email confirmation
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        parent = User.parents.get(pk=uid)
        if token_generator.check_token(parent, token):
            parent.is_active = True
            parent.save()
            messages.success(
                request,
                "Account activated successfully! You can now login.",
            )
            send_parent_signup_confirmation_success_email(request, parent)
        else:
            messages.error(
                request,
                "Activation link is invalid.",
            )
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(
            request,
            "Activation link is invalid.",
        )

    return redirect("accounts:login")


# View for parent user registration with profile information
@parent_required
def parent_dashboard(request):
    parent = request.user
    parent_profile = ParentProfile.objects.get(parent=parent)
    children_profiles = parent_profile.childprofile_set.all()

    context = {
        "parent": parent,
        "children_profiles": children_profiles,
        "parent_profile": parent_profile,
    }
    template_name = "accounts/parent_dashboard.html"

    return render(request, template_name, context)


# View for parent user registration with profile information
@parent_required
def parent_profile(request):
    parent = request.user
    parent_profile = parent.parentprofile
    children_profiles = parent_profile.childprofile_set.all()

    context = {
        "parent": parent,
        "children_profiles": children_profiles,
        "profile": parent_profile,
    }
    template_name = "accounts/parent_profile.html"

    return render(request, template_name, context)


# View for child profile
@child_required
def child_profile(request):
    child = request.user
    child_profile = child.childprofile
    parent_profile = child_profile.parent_profile

    context = {
        "child": child,
        "profile": child_profile,
        "parent_profile": parent_profile,
    }
    template_name = "accounts/child_profile.html"

    return render(request, template_name, context)


# update parent details
@parent_required
def update_parent_info(request):
    if request.method == "POST":
        # Get the parent's profile instance for the logged-in user
        parent = request.user
        parent_profile = request.user.parentprofile
        # Extract data from the POST request
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        gender = request.POST.get("gender")

        # Update the parent's info fields with the extracted data
        parent.username = username
        parent.first_name = first_name
        parent.last_name = last_name
        parent.save()

        # Update the parent's profile fields with the extracted data
        parent_profile.gender = gender
        parent_profile.save()

        messages.success(request, "Parent info updated successfully.")

    else:
        messages.error(request, "You don't have access to this page")

    return redirect("accounts:parent_profile")


# update child details
@child_required
def update_child_info(request):
    if request.method == "POST":
        # Get the parent's profile instance for the logged-in user
        child = request.user
        child_profile = child.childprofile
        # Extract data from the POST request
        username = request.POST.get("username")

        # Update the parent's info fields with the extracted data
        child.username = username
        child.save()

        # Update the parent's profile fields with the extracted data
        messages.success(request, "Child info updated successfully.")

    else:
        messages.error(request, "You don't have access to this page")

    return redirect("accounts:child_profile")


# update parent contact info details
@parent_required
def update_parent_contacts(request):
    if request.method == "POST":
        # Get the parent's profile instance for the logged-in user
        parent = request.user
        parent_profile = request.user.parentprofile
        # Extract data from the POST request
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")

        # Update the parent's info fields with the extracted data
        parent.email = email
        parent.save()

        # Update the parent's profile fields with the extracted data
        parent_profile.address = address
        parent_profile.phone_number = phone_number
        parent_profile.save()

        messages.success(request, "Parent contact details updated successfully.")

    else:
        messages.error(request, "You don't have access to this page")

    return redirect("accounts:parent_profile")


# update parent profile photo view
@parent_required
def update_profile_photo(request):
    if request.method == "POST":
        # Retrieve the current user's parent profile
        parent = request.user
        parent_profile = ParentProfile.objects.get(parent=parent)

        # Handle the uploaded photo
        new_photo = request.FILES.get("profile_photo")

        # Update the profile photo
        if new_photo:
            parent_profile.photo = new_photo
            parent_profile.save()
            messages.success(request, "Profile photo updated successfully.")
        else:
            messages.error(request, "Please select a valid photo.")

    else:
        messages.error(request, "You don't have access to this page")

    return redirect("accounts:parent_profile")


# View for child user registration with profile information
@child_required
def child_dashboard(request):
    child = request.user
    child_profile = ChildProfile.objects.get(child=child)

    context = {"child": child, "child_profile": child_profile}
    template_name = "accounts/child_dashboard.html"

    return render(request, template_name, context)


@parent_required
def register_child(request):
    parent = request.user

    if request.method == "POST":
        try:
            child_form = ChildRegistrationForm(request.POST)
            child_profile_form = ChildProfileForm(request.POST)
            if child_form.is_valid() and child_profile_form.is_valid():
                child = child_form.save(commit=False)
                child.user_type = User.UserType.CHILD
                profile = child_profile_form.save(commit=False)
                profile.child = child
                profile.account_status = AccountStatus.ACTIVE
                profile.parent_profile = parent.parentprofile
                child.email = parent.email
                child.save()
                profile.save()
                messages.success(
                    request,
                    f"Child {child.get_full_name()} Has Been Registered Successfully",
                )
                send_child_signup_email(request, parent, child)
                return redirect("accounts:parent_dashboard")
        except ValidationError as e:
            # Handle form validation errors and display them as part of the response
            messages.error(request, str(e.message))
            return redirect("accounts:register_child")
        except Exception as e:
            # Handle other exceptions or errors
            messages.error(request, "An error occurred during registration.")
            return redirect("accounts:register_child")

    else:
        child_form = ChildRegistrationForm()
        child_profile_form = ChildProfileForm()

    template_name = "registration/child_registration.html"
    context = {"child_form": child_form, "child_profile_form": child_profile_form}
    return render(request, template_name, context)


# parent change password
@parent_required
def parent_password_change(request):
    parent = request.user

    if request.method == "POST":
        form = PasswordChangeForm(parent, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("accounts:parent_profile")
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "accounts/parent_password_change.html", {"form": form})
