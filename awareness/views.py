from django.shortcuts import render, redirect

from accounts.decorators import child_required, parent_required
from django.contrib.auth.decorators import login_required


@child_required # restrict access to child only
def intro(request):
    child = request.user
    child_profile = child.childprofile

    template_name = "awareness/intro.html"
    context = {"child": child, "profile": child_profile}
    return render(request, template_name, context)

@child_required # restrict access to child only
def bahati(request):
    child = request.user
    child_profile = child.childprofile

    template_name = "awareness/bahati.html"
    context = {"child": child, "profile": child_profile}
    return render(request, template_name, context)


@child_required # restrict access to child only
def klein(request):
    child = request.user
    child_profile = child.childprofile

    template_name = "awareness/klein.html"
    context = {"child": child, "profile": child_profile}
    return render(request, template_name, context)


@child_required # restrict access to child only
def meki(request):
    child = request.user
    child_profile = child.childprofile

    template_name = "awareness/meki.html"
    context = {"child": child, "profile": child_profile}
    return render(request, template_name, context)
