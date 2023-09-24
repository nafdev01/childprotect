# safesearch/filter.py
import requests
from safesearch.models import BannedWord
from django.template.loader import get_template
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


def get_results(api_key, custom_search_engine_id, query):
    search_results = list()

    # Make a request to the Google Custom Search API.
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={custom_search_engine_id}&q={query}&num=10"

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


def word_banned_by_parent(user_word, banned_by):
    banned_word = BannedWord.objects.filter(word=user_word, banned_by=banned_by).first()
    return banned_word is not None


def word_banned_by_default(user_word):
    banned_word = BannedWord.objects.filter(word=user_word, banned_default=True).first()
    return banned_word is not None


def get_allowed(value):
    if value:
        return "Yes"
    else:
        return "No"
