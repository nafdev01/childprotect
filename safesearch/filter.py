# safesearch/filter.py
import requests
from safesearch.models import BannedWord
from django.template.loader import get_template
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib import messages


def get_results(api_key, custom_search_engine_id, query, num_results):
    search_results = list()

    # Make a request to the Google Custom Search API.
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={custom_search_engine_id}&q={query}&num={num_results}"

    response = requests.get(url)

    # Parse and process the response (e.g., extract search results).
    if response.status_code == 200:
        data = response.json()

        # Check if there are search results
        if "items" in data:
            # Iterate through the search results and print them
            for index, item in enumerate(data["items"], start=1):
                search_result = {
                    "index": index,
                    "title": item["title"],
                    "link": item["link"],
                    "snippet": item["snippet"],
                }
                search_results.append(search_result)

            return search_results  # Return the list of search results

        else:
            print("No search results found.")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None


def is_word_banned(user_word, banned_by):
    try:
        banned_word = BannedWord.objects.get(word=user_word, banned_by=banned_by)
        return True
    except BannedWord.DoesNotExist:
        return False


def send_email_alert(request, flagged_words, search_phrase):
    child = request.user
    parent = child.childprofile.parent_profile.parent
    # Retrieve entry by id
    subject = f"A search by your child {child.get_full_name()} has been flagged"
    sender = settings.EMAIL_HOST_USER
    recipient = parent.email
    message = get_template(
        "safesearch/includes/flagged_search_email_template.html"
    ).render(
        {
            "child": child,
            "flagged_words": flagged_words,
            "search_phrase": search_phrase.phrase.split(),
        }
    )
    mail = EmailMessage(
        subject=subject,
        body=message,
        from_email=sender,
        to=[recipient],
        reply_to=[sender],
    )
    mail.content_subtype = "html"
    if mail.send():
        messages.warning(
            request, f"Your parent has been alerted about your illegal search"
        )
    else:
        messages.error(request, f"Email could not be sent to your parent")


def get_allowed(value):
    if value:
        return "Yes"
    else:
        return "No"
