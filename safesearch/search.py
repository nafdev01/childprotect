# safesearch/filter.py
import requests
from safesearch.models import BannedWord


def filter_search_results(search_results, parent):
    filtered_results = []

    for result in search_results:
        # Check if the title, link, or snippet contains any banned words by default
        title_has_banned_word_default = any(
            word_banned_by_default(word) for word in result["title"].lower().split()
        )
        snippet_has_banned_word_default = any(
            word_banned_by_default(word) for word in result["snippet"].lower().split()
        )

        # Check if the title, link, or snippet contains any banned words by parent
        title_has_banned_word_parent = any(
            word_banned_by_parent(word, banned_by=parent)
            for word in result["title"].split()
        )
        snippet_has_banned_word_parent = any(
            word_banned_by_parent(word, banned_by=parent)
            for word in result["snippet"].split()
        )

        # If none of them have banned words, add the result to filtered_results
        if not (
            title_has_banned_word_default
            or snippet_has_banned_word_default
            or title_has_banned_word_parent
            or snippet_has_banned_word_parent
        ):
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

        else:
            print("No search results found.")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None


def word_banned_by_parent(user_word, banned_by):
    banned_word = BannedWord.banned_by_parent.filter(
        word=user_word, banned_by=banned_by
    ).first()
    return banned_word is not None


def word_banned_by_default(user_word):
    banned_word = BannedWord.banned_by_default.filter(
        word=user_word, default_ban=True
    ).first()
    return banned_word is not None


def get_allowed(value):
    if value:
        return "Yes"
    else:
        return "No"
