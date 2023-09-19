from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import *
from accounts.models import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .filter import get_results, send_email_alert, is_word_banned


@login_required
def search(request):
    # Check if the user is a child
    if request.user.is_child:
        child = request.user
    elif request.user.is_parent:
        messages.error(request, "You need to be a child to access this search engine")
        return redirect("accounts:dashboard")
    else:
        messages.error(request, "You need to be a child to access this search engine")
        return redirect("home")

    search_results = []  # Initialize an empty list

    if request.method == "POST":
        search_query = request.POST.get("search-query")
        no_of_results = request.POST.get("no-of-results")
        searched = True
        flagged_words = list()
        illegal_search = False

        search_phrase = SearchPhrase(
            searched_by=child.childprofile,
            phrase=search_query,
            no_of_results=no_of_results,
        )
        search_phrase.save()

        for word in search_query.split():
            if is_word_banned(word):
                flagged_words.append(word)
                illegal_search = True

        if illegal_search:
            messages.error(
                request, f"You searched for the banned words {flagged_words}"
            )
            send_email_alert(request, flagged_words, search_phrase)
            return redirect("safesearch:child_search_history")

        search_results = get_results(
            settings.GOOGLE_API_KEY,
            settings.CUSTOM_SEARCH_ENGINE_ID,
            search_query,
            no_of_results,
        )

    else:
        searched = False

    template_name = "safesearch/search.html"
    context = {"search_results": search_results, "searched": searched}
    return render(request, template_name, context)


@login_required
def child_search_history(request):
    # Check if the user is a child
    if request.user.user_type == User.UserType.CHILD:
        child = request.user
    elif request.user.user_type == User.UserType.PARENT:
        messages.warning(
            request, "Redirecting you to all your children's search history"
        )
        return redirect("safesearch:parent_search_history")
    else:
        messages.error(request, "You need to be a child to access this page")
        return redirect("home")

    search_phrases = SearchPhrase.objects.filter(searched_by=child.childprofile)

    template_name = "safesearch/child_search_history.html"
    context = {"search_phrases": search_phrases}
    return render(request, template_name, context)


@login_required
def parent_search_history(request):
    # Check if the user is a child
    if request.user.user_type == User.UserType.PARENT:
        parent = request.user
    elif request.user.user_type == User.UserType.CHILD:
        messages.warning(request, "Redirecting you to your search history")
        return redirect("safesearch:child_search_history")
    else:
        messages.error(request, "You need to be a child to access this page")
        return redirect("home")

    search_phrases = SearchPhrase.objects.filter(
        searched_by__parent_profile=parent.parentprofile
    )

    template_name = "safesearch/parent_search_history.html"
    context = {"search_phrases": search_phrases}
    return render(request, template_name, context)


@login_required
def create_banned_word(request):
    # Check if the user is a child
    if request.user.user_type == User.UserType.PARENT:
        parent = request.user
    elif request.user.user_type == User.UserType.CHILD:
        messages.warning(request, "You need to be a parent to ban a word")
        return redirect("safesearch:child_dashboard")
    else:
        messages.error(request, "You need to be a child to access this page")
        return redirect("home")

    if request.method == "POST":
        form = BannedWordForm(request.POST)
        if form.is_valid():
            banned_word = form.save(commit=False)
            banned_word.banned_by = parent.parentprofile
            banned_word.save()
            messages.success(request, f"You have banned the word {banned_word}")
            return redirect("safesearch:banned_words")
    else:
        form = BannedWordForm()

    return render(request, "safesearch/banned_word_create.html", {"form": form})


@login_required
def banned_word_list(request):
    # Check if the user is a child
    if request.user.user_type == User.UserType.PARENT:
        parent = request.user.parentprofile
    elif request.user.user_type == User.UserType.CHILD:
        child = request.user
        parent = child.childprofile.parent_profile
    else:
        messages.error(request, "You need to be a child or parent to access this page")
        return redirect("home")

    banned_words = BannedWord.objects.filter(banned_by=parent)

    template_name = ("safesearch/banned_words.html",)
    context = {"banned_words": banned_words}
    return render(request, template_name, context)
