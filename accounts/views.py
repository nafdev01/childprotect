import os
import tempfile
from django.shortcuts import render, redirect
from django.urls import reverse
from accounts.decorators import parent_required, child_required, guest_required
from accounts.forms import *
from accounts.notifications import *
from accounts.models import User, ParentProfile, ChildProfile, AccountStatus
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from accounts.models import Confirmation
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from datetime import datetime
from django.core.files import File
from django.contrib.auth.decorators import login_required


# logout view
def logout_view(request):
    messages.success(request, "You have logged out successfully!")
    logout(request)
    return redirect("login")


# login view
@guest_required
def login_user(request):
    if request.method == "POST":
        # Retrieve username and password from POST data
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type")

        if not (username and password and user_type):
            messages.error(request, f"Fill in the form fields as required")
        elif username and password and user_type:
            try:
                if user_type == "parent":
                    parent = User.parents.get(username=username)

                    if not parent.is_active:
                        messages.error(
                            request,
                            f"Please confirm your email at {parent.email[:5]}**************{parent.email[-5:]} before attempting to log in",
                        )
                        return redirect(reverse("login"))
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
                            return redirect("home")
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
                        return redirect(reverse("login"))
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
                            return redirect("home")
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
            return redirect("login")

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

    return redirect("login")


def home(request):
    if not request.user.is_authenticated:
        context = {
            "section": "home",
        }
        template_name = "home.html"

    elif request.user.is_parent:
        parent = request.user
        parent_profile = ParentProfile.objects.get(parent=parent)
        children_profiles = parent_profile.childprofile_set.all()

        context = {
            "parent": parent,
            "children_profiles": children_profiles,
            "parent_profile": parent_profile,
        }
        template_name = "accounts/parent_dashboard.html"
    elif request.user.is_child:
        child = request.user
        child_profile = ChildProfile.objects.get(child=child)

        context = {"child": child, "child_profile": child_profile}
        template_name = "accounts/child_dashboard.html"

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

    return redirect("parent_profile")


# update child details
@child_required
def update_child_profile(request):
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

    return redirect("child_profile")


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

    return redirect("parent_profile")


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

    return redirect("parent_profile")


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
                return redirect("home")
            else:
                # Handle form validation errors for child_form
                for field, error_messages in child_form.errors.items():
                    for error_message in error_messages:
                        messages.error(
                            request, f"Child Form Error - {field}: {error_message}"
                        )

                # Handle form validation errors for child_profile_form
                for field, error_messages in child_profile_form.errors.items():
                    for error_message in error_messages:
                        messages.error(
                            request,
                            f"Child Profile Form Error - {field}: {error_message}",
                        )

                return redirect("register_child")
        except ValidationError as e:
            # Handle form validation errors and display them as part of the response
            messages.error(request, str(e.message))
            return redirect("register_child")
        except Exception as e:
            # Handle other exceptions or errors
            messages.error(request, "An error occurred during registration.")
            return redirect("register_child")

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
            send_parent_password_change_success_email(request, parent)
            return redirect("parent_profile")
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "accounts/parent_password_change.html", {"form": form})


# parent view to see childrens information
@parent_required
def children_details(request):
    parent = request.user
    parent_profile = ParentProfile.objects.get(parent=parent)
    children_profiles = parent_profile.childprofile_set.all()

    context = {
        "parent": parent,
        "children_profiles": children_profiles,
        "parent_profile": parent_profile,
    }
    template_name = "accounts/children_details.html"

    return render(request, template_name, context)


# update child details
@parent_required
def update_child_info(request, child_id):
    if request.method == "POST":
        try:
            # Get the parent's profile instance for the logged-in user
            parent = request.user
            child = User.children.get(id=child_id)
            child_profile = child.childprofile
            # Extract data from the POST request
            username = request.POST.get("username")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            gender = request.POST.get("gender")
            date_of_birth = request.POST.get("date_of_birth")

            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()

            # Update the child's info fields with the extracted data
            child.username = username
            child.first_name = first_name
            child.last_name = last_name
            child.save()

            # Update the child's profile fields with the extracted data
            child_profile.gender = gender
            child_profile.date_of_birth = date_of_birth
            child_profile.save()

            # Update the child's profile fields with the extracted data
            messages.success(
                request, f"{child.get_full_name()} info updated successfully."
            )
        except ValidationError as e:
            # Handle form validation errors and display them as part of the response
            messages.error(request, str(e.message))
            return redirect("children_details")
        except Exception as e:
            # Handle other exceptions or errors
            error_message = str(e)  # Get the exception message as a string
            messages.error(request, error_message)  # Display the exception message
            print(error_message)  # Display the exception message
            return redirect("children_details")

    else:
        messages.error(request, "You don't have access to this page")

    return redirect("children_details")


# parent change password
@parent_required
def update_child_password(request, child_id):
    parent = request.user
    child = User.children.get(id=child_id)

    if request.method == "POST":
        try:
            form = SetPasswordForm(child, request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(
                    request, f"{child.get_full_name()} password changed successfully"
                )
            else:
                # Handle form validation errors for child_form
                for field, error_messages in form.errors.items():
                    error_list = list()
                    for error_message in error_messages:
                        error_list.append(error_message)

                error_message = "".join(error_list).lower().replace("the", "this")

                messages.error(
                    request, f"Password Form Error - {error_message.title()}"
                )

        except Exception as e:
            messages.error(request, f"{e}")

    return redirect("children_details")


# update child avatar view
@login_required
def update_avatar(request, child_id):
    if request.method == "POST":
        child = User.children.get(id=child_id)
        # Retrieve the current user's parent profile
        child_profile = ChildProfile.objects.get(child=child)

        # Handle the uploaded photo
        avatar = request.POST.get("avatar")

        avatar_options = {
            "avatar1": "avatars/avatar1.png",
            "avatar2": "avatars/avatar2.png",
            "avatar3": "avatars/avatar3.png",
            "avatar4": "avatars/avatar4.png",
            "avatar5": "avatars/avatar5.png",
            "avatar6": "avatars/avatar6.png",
        }

        if avatar not in avatar_options.keys():
            messages.error(request, f"Avatar name error in form --- {avatar}")
        else:
            # Generate a temporary file path for the avatar

            # Construct the full path to the selected avatar
            avatar_path = os.path.join(settings.MEDIA_ROOT, avatar_options.get(avatar))
            print(f"FILE PATH: {avatar_path}")

            # Copy the avatar image to the temporary file
            with open(avatar_path, "rb") as avatar_file:
                child_profile.avatar = File(avatar_file)
                child_profile.save()

            messages.success(request, "Avatar updated successfully.")
    else:
        messages.error(request, "You don't have access to this page")

    if request.user.is_parent:
        return redirect("children_details")
    elif request.user.is_child:
        return redirect("child_profile")
