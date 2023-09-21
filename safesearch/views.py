from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import *
from accounts.models import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .filter import get_results, send_email_alert, is_word_banned
from django.utils import timezone
import csv


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
        safe = True

        for word in search_query.split():
            if is_word_banned(word, child.childprofile.parent_profile):
                flagged_words.append(word)
                safe = False

        search_phrase = SearchPhrase(
            searched_by=child.childprofile,
            phrase=search_query,
            no_of_results=no_of_results,
            allowed=safe,
        )
        search_phrase.save()

        if not safe:
            messages.error(
                request, f"You searched for the banned words {flagged_words}"
            )

            flagged_search = FlaggedSearch(search_phrase=search_phrase)
            flagged_search.save()

            flagged_alert = FlaggedAlert(flagged_search=flagged_search)
            flagged_alert.save()

            for flagged_word in flagged_words:
                banned_word = BannedWord.objects.get(
                    word=flagged_word.lower(),
                    banned_by=child.childprofile.parent_profile,
                )
                FlaggedWord(
                    flagged_search=flagged_search, flagged_word=banned_word
                ).save()

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
    else:
        messages.error(request, "You need to be a parent to access this page")
        return redirect("home")

    banned_words = BannedWord.objects.filter(banned_by=parent)

    template_name = ("safesearch/banned_words.html",)
    context = {"banned_words": banned_words}
    return render(request, template_name, context)


@login_required
def alert_list(request):
    # Check if the user is a child
    if request.user.user_type == User.UserType.PARENT:
        parent_profile = request.user.parentprofile
    else:
        messages.error(request, "You need to be a parent to access this page")
        return redirect("home")

    flagged_alerts = FlaggedAlert.objects.filter(reviewed_by=parent_profile)
    alert_count = FlaggedAlert.objects.filter(
        flagged_search__search_phrase__searched_by__parent_profile_id=parent_profile.id,
        been_reviewed=False,
    ).count()

    if alert_count > 1:
        messages.info(request, f"You have {alert_count} unreviewed alerts")
    elif alert_count == 1:
        messages.warning(request, "You have one unreviewed alert")

    template_name = ("safesearch/flagged_alerts.html",)
    context = {"alerts": flagged_alerts}
    return render(request, template_name, context)


@login_required
def review_alert(request, alert_id):
    # Check if the user is a child
    if request.user.user_type == User.UserType.PARENT:
        parent_profile = request.user.parentprofile
    else:
        messages.error(request, "You need to be a parent to access this page")
        return redirect("home")

    alert = FlaggedAlert.objects.get(id=alert_id)

    if alert:
        if not alert.been_reviewed:
            alert.been_reviewed = True
            alert.reviewed_on = timezone.now()
            alert.save()
            messages.success(request, "Alert reviewed successfully")
        else:
            messages.error(request, "Alert has already been reviewed")
    else:
        messages.error(request, "Alert not reviewed. Error occurred")

    return redirect("safesearch:alert_list")


def add_banned_csv(request):
    if request.method == "POST":
        form = BannedCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data["csv_file"]
            # Process the CSV file and add banned words to the database
            if csv_file:
                decoded_file = csv_file.read().decode("utf-8")
                csv_data = csv.reader(decoded_file.splitlines(), delimiter=",")
                for row in csv_data:
                    for word in row:
                        if not BannedWord.objects.filter(
                            word=word,
                            banned_by=request.user.parentprofile,
                        ):
                            banned_word = BannedWord(
                                banned_by=request.user.parentprofile,
                                word=word,
                                reason=BanReason.INAPPROPRIATE_CONTENT,
                            )
                            banned_word.save()
            messages.success(
                request, "Successfully uploaded banned words from csv file"
            )
            return redirect("safesearch:banned_words")
    else:
        form = BannedCSVForm()
    return render(request, "safesearch/add_banned_csv.html", {"form": form})
