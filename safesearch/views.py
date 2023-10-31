import csv
import datetime
import os
from io import BytesIO

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from accounts.decorators import child_required, parent_required
from accounts.models import *
from accounts.notifications import send_email_flagged_alert, send_email_suspicious_alert
from safesearch.forms import *
from safesearch.models import *
from safesearch.search import (
    create_flagged_alert,
    create_flagged_words,
    get_results,
    is_within_time_range,
    word_is_banned,
)


# child search functionality
@child_required
def search(request):
    child = request.user
    child_profile = child.childprofile
    parent = child.childprofile.parent_profile

    search_results = []  # Initialize an empty list
    # Get the current time
    current_time = timezone.now().time()

    # Define the search time boundaries
    search_time_start = child.childprofile.search_time_start
    search_time_end = child.childprofile.search_time_end

    if request.method == "GET":
        search_query = request.GET.get("search-query")
        if search_query:
            if not is_within_time_range(
                current_time, search_time_start, search_time_end
            ):
                messages.error(request, "Search is not allowed at this time.")
                return redirect("search")
            searched = True
            flagged_words = list()
            safe = True

            for word in search_query.lower().split():
                if word_is_banned(word, child.childprofile.parent_profile):
                    flagged_words.append(word)
                    safe = False

            if safe:
                search_status = SearchStatus.SAFE
            else:
                search_status = SearchStatus.FLAGGED

            search_phrase = SearchPhrase(
                searched_by=child.childprofile,
                phrase=search_query,
                search_status=search_status,
            )
            search_phrase.save()

            search_results, suspicious_results = get_results(
                settings.GOOGLE_API_KEY,
                settings.CUSTOM_SEARCH_ENGINE_ID,
                search_query,
                parent,
            )
            if not safe:
                create_flagged_alert(search_phrase)

                create_flagged_words(search_phrase, flagged_words, child)

                if send_email_flagged_alert(request, flagged_words, search_phrase):
                    messages.warning(
                        request,
                        f"Your search contained the banned words { ','.join(flagged_words)}",
                    )
            else:
                if len(suspicious_results) >= 2:
                    search_phrase.search_status = SearchStatus.SUSPICIOUS
                    search_phrase.save()
                    send_email_suspicious_alert(
                        request, suspicious_results, search_phrase
                    )
                    messages.warning(
                        request,
                        f"Your search returned results that contained banned words!",
                    )

            if child_profile.alert_level == AlertLevel.LOW:
                search_results = search_results + suspicious_results
            elif child_profile.alert_level == AlertLevel.MODERATE:
                if search_phrase.search_status == SearchStatus.SUSPICIOUS:
                    search_results = search_results
                elif search_phrase.search_status == SearchStatus.FLAGGED:
                    return redirect("search")
            elif child_profile.alert_level == AlertLevel.STRICT:
                if search_phrase.search_status == SearchStatus.SUSPICIOUS:
                    return redirect("search")
                elif search_phrase.search_status == SearchStatus.FLAGGED:
                    return redirect("search")

        else:
            searched = False

    template_name = "safesearch/search.html"
    context = {"search_results": search_results, "searched": searched}
    return render(request, template_name, context)


# child can see teir search history
@login_required
def search_history(request, child_id=None):
    context = {}

    if request.user.is_child:
        child = request.user
        child_profile = child.childprofile
        search_phrases = SearchPhrase.objects.filter(searched_by=child.childprofile)
        template_name = "safesearch/child_search_history.html"
        context["child"] = child
        context["child_profile"] = child_profile

    elif request.user.is_parent:
        parent = request.user
        parent_profile = parent.parentprofile
        if child_id:
            search_phrases = SearchPhrase.objects.filter(searched_by_id=child_id)
            context["child_id"] = child_id
        else:
            search_phrases = SearchPhrase.objects.filter(
                searched_by__parent_profile=parent_profile
            )

        template_name = "safesearch/parent_search_history.html"
        context["parent"] = parent
        context["parent_profile"] = parent_profile

    else:
        messages.error(request, "You don't have access to the search history page")
        return redirect("home")

    context["search_phrases"] = search_phrases
    return render(request, template_name, context)


# create banned word view
@method_decorator(parent_required, name="dispatch")
class BannedWordCreateView(CreateView):
    model = BannedWord
    form_class = BannedWordForm
    template_name = "safesearch/banned_word_create.html"

    def form_valid(self, form):
        # Override this method to customize behavior when the form is valid.
        # You can perform additional actions here if needed.
        banned_word = form.save(commit=False)
        banned_word.banned_by = self.request.user.parentprofile
        banned_word.save()
        messages.success(self.request, f"You have banned the word {banned_word}")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["csv_form"] = BannedCSVForm()
        return context

    def get_success_url(self):
        return reverse("create_banned_word")


# uploaded csv file with words to be banned
@parent_required
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
            return redirect("banned_words")
        else:
            messages.error(request, f"There was an error uploading the form")
    else:
        messages.error(request, f"You don't have access to this page")

    return redirect("create_banned_word")


# unban a word
@parent_required
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
    return redirect("banned_words")


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
    return redirect("banned_words")


# parents banned words list
@parent_required
def banned_word_list(request):
    parent = request.user.parentprofile

    word = request.GET.get("word")
    per_page = request.GET.get("per_page")

    if word:
        banned_words_list = BannedWord.objects.filter(
            banned_by=parent, word__contains=word
        )
    else:
        banned_words_list = BannedWord.objects.filter(
            banned_by=parent,
        )

    if per_page:
        # Pagination with 20 banned words per page
        paginator = Paginator(banned_words_list, int(per_page))
        page_number = request.GET.get("page", 1)
    else:
        # Pagination with custom banned words per page
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


# show words from our default banned words list
@parent_required
def default_banned_word_list(request):
    parent = request.user.parentprofile

    # Specify the path to your CSV file
    csv_file_path = os.path.join(settings.MEDIA_ROOT, "default_banned.csv")

    banned_words = []

    # Open and read the CSV file
    with open(csv_file_path, "r") as csv_file:
        csv_data = csv.reader(csv_file, delimiter=",")
        for row in csv_data:
            for word in row:
                banned_words.append(word)  # Assuming the words are in the first column

    word = request.GET.get("word")

    if word:
        banned_words_list = [
            word for word in banned_words if word and word.__contains__(word)
        ]
    else:
        banned_words_list = banned_words

    # Pagination with 20 banned words per page
    paginator = Paginator(banned_words_list, 20)
    page_number = request.GET.get("page", 1)

    try:
        banned_words = paginator.page(page_number)
        banned_words.adjusted_elided_pages = paginator.get_elided_page_range(
            page_number
        )
    except PageNotAnInteger:
        banned_words = paginator.page(1)
    except EmptyPage:
        banned_words = paginator.page(paginator.num_pages)

    template_name = ("safesearch/banned_words_default.html",)
    context = {"banned_words": banned_words}
    return render(request, template_name, context)


# list of flagged alerts
@method_decorator(parent_required, name="dispatch")
class SearchAlertListView(ListView):
    model = SearchAlert
    template_name = "safesearch/flagged_alerts.html"
    context_object_name = "alerts"

    def get_queryset(self):
        parent_profile = self.request.user.parentprofile
        return SearchAlert.objects.filter(reviewed_by=parent_profile)


# mark flagged alert as reviewed
@parent_required
def review_alert(request, alert_id):
    alert = SearchAlert.objects.get(id=alert_id)

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

    return redirect("alert_list")


@parent_required
def generate_pdf_report(request, child_id=None):
    # Fetch the child's search history
    if child_id:
        child = User.children.get(id=child_id)
        search_history = SearchPhrase.objects.filter(searched_by__child_id=child_id)
    else:
        search_history = SearchPhrase.objects.filter(
            searched_by__parent_profile__parent_id=request.user.id
        )

    # Create a BytesIO buffer to receive the PDF content
    buffer = BytesIO()

    # Create the PDF object, using the BytesIO buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))

    # Create a list to hold the table data
    data = [["Searched By", "Search Phrase", "Searched On", "Search Status"]]

    # Populate the data list with search history
    for entry in search_history:
        data.append(
            [
                entry.searched_by.child.get_full_name(),
                entry.phrase,
                entry.searched_on.strftime("%Y-%m-%d %H:%M:%S"),
                entry.get_search_status_display(),
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


# child requests a word be unbanned
@child_required
def create_unban_request(request, banned_word_id):
    child = request.user

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
            return redirect("search_history")
    except BannedWord.DoesNotExist:
        messages.error(request, f"Banned word does not exist")
        return redirect("search_history")

    unban_request = UnbanRequest(
        banned_word=banned_word, requested_by=child.childprofile
    )
    unban_request.save()
    messages.success(
        request,
        f"You have submitted an unban request for the word {banned_word.word} successfully",
    )
    return redirect("home")


# deny unban request
@parent_required
def approve_unban_request(request, unban_request_id):
    parent = request.user

    try:
        unban_request = UnbanRequest.objects.get(id=unban_request_id)
        banned_word = BannedWord.banned.get(id=unban_request.banned_word.id)
    except UnbanRequest.DoesNotExist:
        messages.error(request, f"Unban request does not exist")
        return redirect("unban_requests")
    except BannedWord.DoesNotExist:
        messages.error(request, f"No banned word matches your request")
        return redirect("unban_requests")

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

    return redirect("unban_requests")


# deny unban request view
@parent_required
def deny_unban_request(request, unban_request_id):
    parent = request.user

    try:
        unban_request = UnbanRequest.objects.get(id=unban_request_id)
        banned_word = BannedWord.objects.get(id=unban_request.banned_word.id)
    except UnbanRequest.DoesNotExist:
        messages.error(request, f"Unban request does not exist")
        return redirect("unban_requests")
    except BannedWord.DoesNotExist:
        messages.error(request, f"No banned word matches your request")
        return redirect("unban_requests")

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

    return redirect("unban_requests")


# unban request list view
@method_decorator(parent_required, name="dispatch")
class UnbanRequestListView(ListView):
    model = UnbanRequest
    template_name = "safesearch/unban_requests.html"
    context_object_name = "unban_requests"

    def get_queryset(self):
        parent = self.request.user
        unban_requests = UnbanRequest.objects.filter(
            requested_by__parent_profile__parent_id=parent.id
        )
        return unban_requests
