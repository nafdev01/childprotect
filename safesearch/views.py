from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from safesearch.forms import *
from accounts.models import *
from safesearch.models import *
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.conf import settings
from safesearch.search import (
    get_results,
    word_is_banned,
    get_allowed,
)
from accounts.notifications import send_email_flagged_alert, send_email_suspicious_alert
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from safesearch.models import SearchPhrase
import csv


@login_required
def search(request):
    # Check if the user is a child
    if request.user.is_child:
        child = request.user
        parent = child.childprofile.parent_profile

    elif request.user.is_parent:
        messages.error(request, "You need to be a child to access this search engine")
        return redirect("accounts:parent_dashboard")
    else:
        messages.error(request, "You need to be a child to access this search engine")
        return redirect("home")

    search_results = []  # Initialize an empty list

    if request.method == "GET":
        search_query = request.GET.get("search-query")
        if search_query:
            searched = True
            flagged_words = list()
            safe = True

            for word in search_query.lower().split():
                if word_is_banned(word, child.childprofile.parent_profile):
                    flagged_words.append(word)
                    safe = False

            search_phrase = SearchPhrase(
                searched_by=child.childprofile,
                phrase=search_query,
                allowed=safe,
            )
            search_phrase.save()

            if not safe:
                messages.error(
                    request,
                    f"You searched for the banned words { ','.join(flagged_words)}",
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
                    flagged_word = FlaggedWord(
                        flagged_search=flagged_search, flagged_word=banned_word
                    )
                    flagged_word.save()

                send_email_flagged_alert(request, flagged_words, search_phrase)
                return redirect("safesearch:child_search_history")

            else:
                search_results, suspicious_results = get_results(
                    settings.GOOGLE_API_KEY,
                    settings.CUSTOM_SEARCH_ENGINE_ID,
                    search_query,
                    parent,
                )
                if len(suspicious_results) >=5:
                    send_email_suspicious_alert(request, suspicious_results, search_phrase)
                    messages.warning(request, f"Your search was flagged as suspicious and your parent has been alerted")

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


# unban a word
def unban_word(request, word_id):
    parent = request.user
    parent = request.user
    parent_profile = parent.parentprofile
    banned_word = get_object_or_404(BannedWord, id=word_id, banned_by=parent_profile)

    # Mark the word as unbanned
    banned_word.is_banned = False
    banned_word.save()
    messages.success(request, f"You have unbanned the word {banned_word}")

    # Redirect to a success page or the word list
    return redirect("safesearch:banned_words")


# ban a word
def ban_word(request, word_id):
    parent = request.user
    parent_profile = parent.parentprofile
    banned_word = get_object_or_404(BannedWord, id=word_id, banned_by=parent_profile)

    # Mark the word as unbanned
    banned_word.is_banned = True
    banned_word.save()
    messages.success(request, f"You have banned the word {banned_word}")

    # Redirect to a success page or the word list
    return redirect("safesearch:banned_words")


@login_required
def banned_word_list(request):
    # Check if the user is a child
    if request.user.user_type == User.UserType.PARENT:
        parent = request.user.parentprofile
    else:
        messages.error(request, "You need to be a parent to access this page")
        return redirect("home")

    word = request.GET.get("word")

    if word:
        banned_words_list = BannedWord.objects.filter(
            banned_by=parent, word__contains=word
        )
    else:
        banned_words_list = BannedWord.objects.filter(
            banned_by=parent,
        )

    # Pagination with 20 banned words per page
    paginator = Paginator(banned_words_list, 20)
    page_number = request.GET.get("page", 1)

    # Try to open the page
    try:
        banned_words = paginator.page(page_number)
        banned_words.adjusted_elided_pages = paginator.get_elided_page_range(
            page_number
        )

    # If page_number is not an integer deliver the first page
    except PageNotAnInteger:
        banned_words = paginator.page(1)

    # If page_number is out of range deliver last page of results
    except EmptyPage:
        banned_words = paginator.page(paginator.num_pages)

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
                        if (
                            not BannedWord.objects.filter(
                                word=word.strip(),
                                banned_by=request.user.parentprofile,
                            )
                            and word != ""
                        ):
                            banned_word = BannedWord(
                                banned_by=request.user.parentprofile,
                                word=word.strip(),
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


@login_required
def generate_pdf_report(request, child_id=None):
    # Fetch the child's search history
    if child_id:
        child = User.children.get(id=child_id)
        child_search_history = SearchPhrase.objects.filter(
            searched_by__child_id=child_id
        )
    else:
        child_search_history = SearchPhrase.objects.filter(
            searched_by__parent_profile__parent_id=request.user.id
        )

    # Create a BytesIO buffer to receive the PDF content
    buffer = BytesIO()

    # Create the PDF object, using the BytesIO buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))

    # Create a list to hold the table data
    data = [["Searched By", "Search Phrase", "Searched On", "Allowed"]]

    # Populate the data list with search history
    for entry in child_search_history:
        data.append(
            [
                entry.searched_by.child.get_full_name(),
                entry.phrase,
                entry.searched_on.strftime("%Y-%m-%d %H:%M:%S"),
                get_allowed(entry.allowed),
            ]
        )

    # Create the table and add style
    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    # Build the PDF document
    elements = []
    elements.append(table)
    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response.
    pdf_content = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type="application/pdf")

    if child_id:
        response[
            "Content-Disposition"
        ] = 'attachment; filename="{0}_search_history.pdf"'.format(child.get_username())
    else:
        response["Content-Disposition"] = 'attachment; filename="search_history.pdf"'

    response.write(pdf_content)

    response.write(pdf_content)

    return response


@login_required
def create_unban_request(request, banned_word_id):
    if request.user.user_type == User.UserType.CHILD:
        child = request.user
    elif request.user.user_type == User.UserType.PARENT:
        messages.warning(request, "You need to be a child to create an unban request")
        return redirect("safesearch:parent_dashboard")

    try:
        banned_word = BannedWord.banned.get(id=banned_word_id)
            # Check if an unban request with the same requested_by and banned_word already exists
        existing_unban_request = UnbanRequest.objects.filter(
            requested_by=child.childprofile,
            banned_word=banned_word,
        )

        if existing_unban_request:
            messages.warning(
                request,
                f"You have already submitted an unban request for this word ({banned_word}).",
            )
            return redirect("safesearch:child_search_history")
    except BannedWord.DoesNotExist:
        messages.error(request, f"Banned word does not exist")
        return redirect("accounts:child_search_history")

    unban_request = UnbanRequest(
        banned_word=banned_word, requested_by=child.childprofile
    )
    unban_request.save()
    messages.success(
        request,
        f"You have submitted an unban request for the word {banned_word.word} successfully",
    )
    return redirect("accounts:child_dashboard")


@login_required
def approve_unban_request(request, unban_request_id):
    if request.user.user_type == User.UserType.PARENT:
        parent = request.user
    elif request.user.user_type == User.UserType.CHILD:
        messages.warning(request, "You need to be a parent to approve an unban request")
        return redirect("safesearch:child_dashboard")

    try:
        unban_request = UnbanRequest.objects.get(id=unban_request_id)
        banned_word = BannedWord.banned.get(id=unban_request.banned_word.id)
    except UnbanRequest.DoesNotExist:
        messages.error(request, f"Unban request does not exist")
        return redirect("safesearch:unban_requests")
    except BannedWord.DoesNotExist:
        messages.error(request, f"No banned word matches your request")
        return redirect("safesearch:unban_requests")

    unban_request.been_reviewed = True
    unban_request.approved = True
    unban_request.reviewed_on = timezone.now()
    unban_request.save()

    banned_word.is_banned = False
    banned_word.save()

    messages.success(
        request,
        f"You have approved the unban request by your child {unban_request.requested_by.child} and unbanned the word {banned_word.word}",
    )

    return redirect("safesearch:unban_requests")


@login_required
def deny_unban_request(request, unban_request_id):
    if request.user.user_type == User.UserType.PARENT:
        parent = request.user
    elif request.user.user_type == User.UserType.CHILD:
        messages.warning(request, "You need to be a parent to approve an unban request")
        return redirect("safesearch:child_dashboard")

    try:
        unban_request = UnbanRequest.objects.get(id=unban_request_id)
        banned_word = BannedWord.objects.get(id=unban_request.banned_word.id)
    except UnbanRequest.DoesNotExist:
        messages.error(request, f"Unban request does not exist")
        return redirect("safesearch:unban_requests")
    except BannedWord.DoesNotExist:
        messages.error(request, f"No banned word matches your request")
        return redirect("safesearch:unban_requests")

    unban_request.been_reviewed = True
    unban_request.approved = False
    unban_request.reviewed_on = timezone.now()
    unban_request.save()

    banned_word.is_banned = True
    banned_word.save()

    messages.success(
        request,
        f"You have denied the unban request by your child {unban_request.requested_by.child} to unban the word {banned_word.word}",
    )

    return redirect("safesearch:unban_requests")


@login_required
def unban_requests(request):
    # Check if the user is a child
    if request.user.user_type == User.UserType.PARENT:
        parent = request.user
    elif request.user.user_type == User.UserType.CHILD:
        messages.error(request, "You need to be a parent to access this page!")
        return redirect("safesearch:parent_search_history")
    else:
        messages.error(request, "You need to be a child to access this page")
        return redirect("home")

    unban_requests = UnbanRequest.objects.filter(
        requested_by__parent_profile__parent_id=parent.id
    )

    template_name = "safesearch/unban_requests.html"
    context = {"unban_requests": unban_requests}
    return render(request, template_name, context)
