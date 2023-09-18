from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import User, ParentProfile, ChildProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import views as auth_views


# parent login view
def login_parent(request):
    if request.user.is_authenticated:
        # redirect to dashboard if parent is already logged in
        messages.warning(request, "You are already logged in.")
        return redirect("accounts:parent_dashboard")

    if request.method != "POST":
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            parent = authenticate(
                request,
                username=username,
                password=password,
            )

            if parent is not None and parent.user_type == User.UserType.PARENT:
                login(request, parent)
                messages.success(request, "Log In Successful!")
                return redirect("accounts:parent_dashboard")
            else:
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
            profile = parent_profile_form.save(commit=False)
            profile.parent = parent
            parent.save()
            profile.save()
            messages.success(request, "Registration Successful! Log in to continue")
            return redirect("accounts:login_parent")

    else:
        parent_form = ParentRegistrationForm()
        parent_profile_form = ParentProfileForm()

    template_name = "registration/parent_registration.html"
    context = {"parent_form": parent_form, "parent_profile_form": parent_profile_form}
    return render(request, template_name, context)


# View for parent user registration with profile information
@login_required
def parent_dashboard(request):
    if request.user.user_type == User.UserType.CHILD:
        # redirect to dashboard if parent is already logged in
        messages.warning(request, "You are already logged in as a child.")
        return redirect("accounts:child_dashboard")

    parent = request.user
    parent_profile = ParentProfile.objects.get(parent=parent)
    children_profile = parent_profile.childprofile_set.all()

    context = {"parent": parent, "children_profile": children_profile, "parent_profile": parent_profile}
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
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(data=request.POST)
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
    else:
        messages.warning(request, "You should be logged in as a parent to add a child.")
        return redirect("accounts:login_parent")
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
            profile.account_status = ChildProfile.AccountStatus.ACTIVE
            profile.parent_profile = parent.parentprofile
            child.email = parent.email
            child.save()
            profile.save()
            messages.success(request, "Registration Successful! Log in to continue")
            return redirect("accounts:parent_dashboard")

    else:
        child_form = ChildRegistrationForm()
        child_profile_form = ChildProfileForm()

    template_name = "registration/child_registration.html"
    context = {"child_form": child_form, "child_profile_form": child_profile_form}
    return render(request, template_name, context)
