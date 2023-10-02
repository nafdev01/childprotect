from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import *
from .notifications import *
from .models import User, ParentProfile, ChildProfile, AccountStatus
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import Confirmation
from django.contrib.auth.decorators import login_required


# parent login view
def login_parent(request):
    if request.user.is_authenticated:
        # Redirect to dashboard if the parent is already logged in
        messages.warning(request, "You are already logged in.")
        return redirect("accounts:parent_dashboard")

    if request.method != "POST":
        form = LoginForm()
    else:
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            try:
                parent = User.objects.get(username=username, is_active=False)

                if not parent.is_active:
                    messages.error(
                        request,
                        f"Please confirm your email at {parent.email[:5]}**************{parent.email[-5:]} before attempting to log in",
                    )
                    redirect(reverse("accounts:login_parent"))
                else:
                    parent = authenticate(
                        request,
                        username=username,
                        password=password,
                    )

                    if parent is not None and parent.user_type == User.UserType.PARENT:
                        login(request, parent)
                        messages.success(request, "Log In Successful!")
                        send_parent_login_email(request)
                        return redirect("accounts:parent_dashboard")
                    else:
                        messages.error(request, "Invalid username or password.")
            except User.DoesNotExist:
                messages.error(request, "Invalid username or password.")

    template_name = "registration/parent_login.html"
    context = {"form": form}
    return render(request, template_name, context)


# View for parent user registration with profile information
def register_parent(request):
    if request.user.is_authenticated:
        # redirect to dashboard if parent is already logged in
        messages.warning(request, "You are already logged in as a parent.")
        return redirect("accounts:parent_dashboard")

    if request.method == "POST":
        parent_form = ParentRegistrationForm(request.POST)
        parent_profile_form = ParentProfileForm(request.POST)
        if parent_form.is_valid() and parent_profile_form.is_valid():
            parent = parent_form.save(commit=False)
            parent.user_type = User.UserType.PARENT
            parent.is_active = False
            profile = parent_profile_form.save(commit=False)
            profile.parent = parent
            parent.save()
            profile.save()

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
            return redirect("accounts:login_parent")

    else:
        parent_form = ParentRegistrationForm()
        parent_profile_form = ParentProfileForm()

    template_name = "registration/parent_registration.html"
    context = {"parent_form": parent_form, "parent_profile_form": parent_profile_form}
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

    return redirect("accounts:login_parent")


# View for parent user registration with profile information
@login_required
def parent_dashboard(request):
    if request.user.user_type == User.UserType.CHILD:
        # redirect to dashboard if parent is already logged in
        messages.warning(request, "You are already logged in as a child.")
        return redirect("accounts:child_dashboard")

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


# child login view
def login_child(request):
    if request.user.is_authenticated:
        if request.user.user_type == User.UserType.CHILD:
            # redirect to dashboard if parent is already logged in
            messages.warning(request, "You are already logged in as a child.")
            return redirect("accounts:child_dashboard")
        elif request.user.user_type == User.UserType.PARENT:
            # redirect to dashboard if parent is already logged in
            messages.warning(request, "You are already logged in as a parent.")
            return redirect("accounts:parent_dashboard")

    if request.method != "POST":
        form = LoginForm()
    else:
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            child = authenticate(
                request,
                username=username,
                password=password,
            )

            if child is not None and child.user_type == User.UserType.CHILD:
                login(request, child)
                messages.success(request, "Log In Successful!")
                send_child_login_email(request)
                return redirect("accounts:child_dashboard")
            else:
                messages.error(request, "Invalid username or password.")

    template_name = "registration/child_login.html"
    context = {"child_login_form": form}
    return render(request, template_name, context)


# View for child user registration with profile information
@login_required
def child_dashboard(request):
    if request.user.user_type == User.UserType.PARENT:
        # redirect to dashboard if parent is already logged in
        messages.warning(request, "You are already logged in as a parent.")
        return redirect("accounts:parent_dashboard")

    child = request.user
    child_profile = ChildProfile.objects.get(child=child)

    context = {"child": child, "child_profile": child_profile}
    template_name = "accounts/child_dashboard.html"

    return render(request, template_name, context)


# View for parent user registration with profile information
def register_child(request):
    if request.user.is_authenticated:
        if request.user.user_type == User.UserType.CHILD:
            # redirect to dashboard if parent is already logged in
            messages.warning(request, "You are already logged in as a child.")
            return redirect("accounts:child_dashboard")
        else:
            parent = request.user
    else:
        messages.warning(request, "You should be logged in as a parent to add a child.")
        return redirect("accounts:login_parent")

    if request.method == "POST":
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

    else:
        child_form = ChildRegistrationForm()
        child_profile_form = ChildProfileForm()

    template_name = "registration/child_registration.html"
    context = {"child_form": child_form, "child_profile_form": child_profile_form}
    return render(request, template_name, context)
