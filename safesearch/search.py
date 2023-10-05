# safesearch/filter.py
import requests
from safesearch.models import BannedWord
from django.template.loader import get_template
import re


def word_is_banned(word, banned_by):
    banned_word = BannedWord.objects.filter(
        word=word.lower(), banned_by=banned_by
    ).first()
    return banned_word is not None


def split_string(text):
    # Define a regular expression pattern to match commas, full stops, exclamation marks, or spaces
    pattern = r"[,\.\s!]+"

    # Use the re.split() function to split the text based on the pattern
    words = re.split(pattern, text)

    # Remove any empty strings from the result
    words = [word for word in words if word.strip()]

    return words


def filter_search_results(search_results, parent):
    filtered_results = []

    for result in search_results:
        # Split the title and snippet using split_string function
        title_words = split_string(result["title"])
        snippet_words = split_string(result["snippet"])

        # Check if the title or snippet contains any banned words by default
        title_has_banned_word = any(
            word_is_banned(word, banned_by=parent) for word in title_words
        )
        snippet_has_banned_word = any(
            word_is_banned(word, banned_by=parent) for word in snippet_words
        )

        # If none of them have banned words, add the result to filtered_results
        if not (title_has_banned_word or snippet_has_banned_word):
            filtered_results.append(result)

    return filtered_results


def get_results(api_key, custom_search_engine_id, query, parent):
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

            filtered_search_results = filter_search_results(search_results, parent)
            return filtered_search_results

            return search_results  # Return the list of search results

        else:
            print("No search results found.")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None


def get_allowed(value):
    if value:
        return "Yes"
    else:
        return "No"
