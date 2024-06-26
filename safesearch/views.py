import csv
import datetime
import logging
import os
from io import BytesIO

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView
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
    get_banned_phrases,
    get_results,
    has_banned_phrase,
    is_within_time_range,
    word_is_banned,
)

channel_layer = get_channel_layer()
logger = logging.getLogger(__name__)


# child search functionality
@child_required
def search(request):
    child = request.user
    child_profile = child.childprofile
    parent_profile = child_profile.parent_profile
    parent = parent_profile.parent
    context = dict()
    context["parent"] = parent

    search_results = []
    current_time = datetime.datetime.now().time()

    # Define the search time boundaries
    search_time_start = child_profile.search_time_start
    search_time_end = child_profile.search_time_end

    if request.method == "GET":
        search_query = request.GET.get("search-query")
        if search_query:
            if not is_within_time_range(
                current_time, search_time_start, search_time_end
            ):
                messages.error(
                    request,
                    f"Search is not allowed at this time. You can only search between {search_time_start.strftime('%H:%M:%S')} and {search_time_end.strftime('%H:%M:%S')} and the time now is {current_time.strftime('%H:%M:%S')}",
                )

                return redirect("search")
            searched = True
            flagged_words = list()
            safe = True

            for word in search_query.lower().split():
                if word_is_banned(word, child.childprofile):
                    flagged_words.append(word)
                    safe = False

            if has_banned_phrase(search_query.lower(), child_profile):
                flagged_phrases = get_banned_phrases(
                    search_query.lower(), child_profile
                )
                for phrase in flagged_phrases:
                    flagged_words.append(phrase)
                safe = False

            if safe:
                search_status = SearchStatus.SAFE
            else:
                search_status = SearchStatus.FLAGGED
                try:
                    group_name = f"search_alerts_{child.id}"
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            "type": "sendBannedAlert",
                            "title": f"A search by your child {child.get_full_name()} contained banned words!",
                            "username": child.get_username(),
                            "text": f"The banned words '{ ','.join(flagged_words)}' were found in the search '{search_query}' ",
                            "search_phrase": search_query,
                        },
                    )
                    logger.warning(f"Error: sent banned tex message")

                except Exception as e:
                    print(e)
                    logger.warning(f"Error on banned: {e}")

            search_phrase = SearchPhrase(
                searched_by=child_profile,
                phrase=search_query,
                search_status=search_status,
            )
            search_phrase.save()
            context["search_phrase"] = search_phrase

            search_results, suspicious_results = get_results(
                settings.GOOGLE_API_KEY,
                settings.CUSTOM_SEARCH_ENGINE_ID,
                search_query,
                child_profile,
            )
            if not safe:
                create_flagged_alert(search_phrase)

                create_flagged_words(search_phrase, flagged_words, child_profile)

                if send_email_flagged_alert(request, flagged_words, search_phrase):
                    messages.warning(
                        request,
                        f"Your search contained the banned words { ','.join(flagged_words)}",
                    )
            else:
                if len(suspicious_results) >= 2:
                    search_phrase.search_status = SearchStatus.SUSPICIOUS
                    search_phrase.save()
                    try:
                        group_name = f"search_alerts_{child.id}"
                        async_to_sync(channel_layer.group_send)(
                            group_name,
                            {
                                "type": "sendSuspiciousAlert",
                                "title": f"A search by your child {child.get_full_name()} returned results which contained banned words!",
                                "username": child.get_username(),
                                "text": f"The search was '{search_query}'\n",
                                "search_phrase": search_query,
                            },
                        )
                    except Exception as e:
                        print(e)
                        logger.warning(f"Error on banned: {e}")

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
    context["search_results"] = search_results
    context["searched"] = searched
    return render(request, template_name, context)


# child can see their search history
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
@parent_required
def create_banned_word(request):
    parent = request.user
    parent_profile = parent.parentprofile
    children_profiles = ChildProfile.objects.filter(parent_profile=parent_profile)

    if request.method == "POST":
        try:
            words = request.POST.get("word")
            reason = request.POST.get("reason")
            child_profile_ids = request.POST.getlist("ban_for")
            children = list()
        except Exception as e:
            messages.success(request, f"{e}")
            return redirect("create_banned_word")

        for child_profile_id in child_profile_ids:
            try:
                for word in words.split(","):
                    child_profile = ChildProfile.objects.get(id=child_profile_id)
                    banned_word = BannedWord(
                        word=word.strip(),
                        reason=reason,
                        banned_for=child_profile,
                        banned_by=parent_profile,
                    )
                    banned_word.save()
                    if child_profile.child.get_full_name() not in children:
                        children.append(child_profile.child.get_full_name())
            except IntegrityError as e:
                continue
            except ValidationError as e:
                messages.success(request, f"{e}")
                return redirect("create_banned_word")
            except Exception as e:
                messages.success(request, f"{e}")
                return redirect("create_banned_word")

        messages.success(
            request,
            f"Words banned successfully",
        )
        return redirect("banned_words")

    context = {"csv_form": BannedCSVForm(), "children_profiles": children_profiles}
    return render(request, "safesearch/banned_word_create.html", context)


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
                                reason=BanReason.VIOLENT_AND_DISTURBING_CONTENT,
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


# default banned words list
@parent_required
def default_banned_word_list(request):
    parent = request.user
    parent_profile = ParentProfile.objects.get(parent=parent)

    # get parent's children
    children_profiles = parent_profile.childprofile_set.all()

    default_banned_words = BannedDefault.objects.all()

    template_name = ("safesearch/banned_words_default.html",)
    context = {
        "default_banned_words": default_banned_words,
        "children_profiles": children_profiles,
    }
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
    if child_id:
        child = User.children.get(id=child_id)
        search_history = SearchPhrase.objects.filter(searched_by__child_id=child_id)
    else:
        search_history = SearchPhrase.objects.filter(
            searched_by__parent_profile__parent_id=request.user.id
        )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
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

    elements = []
    elements.append(table)
    doc.build(elements)
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
        ).first()

        if existing_unban_request:
            messages.warning(
                request,
                f"You have already submitted an unban request for this word ({banned_word}).",
            )
            try:
                group_name = f"unban_requests_{child.id}"
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "sendUnbanRequest",
                        "type_of_request": "unban_request",
                        "title": f"Your child {child.get_full_name()} has submitted an unban request!",
                        "child": child.get_username(),
                        "word": f"{banned_word.word}",
                        "banned_word_id": banned_word_id,
                        "unban_request_id": existing_unban_request.id,
                    },
                )
            except Exception as e:
                print(e)
                logger.warning(f"Error on banned: {e}")
            return redirect("search_history")
    except BannedWord.DoesNotExist:
        messages.error(request, f"Banned word does not exist")
        return redirect("search_history")

    unban_request = UnbanRequest(
        banned_word=banned_word, requested_by=child.childprofile
    )
    unban_request.save()
    try:
        group_name = f"unban_requests_{child.id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "sendUnbanRequest",
                "type_of_request": "unban_request",
                "title": f"Your child {child.get_full_name()} has submitted an unban request!",
                "child": child.get_username(),
                "word": f"{banned_word.word}",
                "banned_word_id": banned_word_id,
                "unban_request_id": unban_request.id,
            },
        )
    except Exception as e:
        print(e)
        logger.warning(f"Error on banned: {e}")

    messages.success(
        request,
        f"You have submitted an unban request for the word {banned_word.word}",
    )
    return redirect("search_history")


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
@login_required
def unban_requests(request):
    context = dict()
    if request.user.is_child:
        child = request.user
        child_profile = child.childprofile

        unban_requests = UnbanRequest.objects.filter(requested_by=child_profile)
        context["unban_requests"] = unban_requests
        template_name = "safesearch/child_unban_requests.html"
    elif request.user.is_parent:
        parent = request.user
        parent_profile = parent.parentprofile

        unban_requests = UnbanRequest.objects.filter(
            requested_by__parent_profile__parent_id=parent.id
        )
        template_name = "safesearch/unban_requests.html"
        context["unban_requests"] = unban_requests
    else:
        messages.error(request, f"You dont have access to this page!")
        return redirect("home")

    return render(request, template_name, context)
