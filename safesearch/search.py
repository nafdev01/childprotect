# safesearch/filter.py
import requests
from safesearch.models import BannedType, BannedWord, FlaggedWord, SearchAlert
from django.template.loader import get_template
import re
import logging

logger = logging.getLogger(__name__)


def is_word_or_phrase(input_string):
    input_string = input_string.strip()
    if " " in input_string:
        return BannedType.PHRASE
    else:
        return BannedType.WORD


def create_flagged_alert(search_phrase):
    flagged_alert = SearchAlert(flagged_search=search_phrase)
    flagged_alert.save()


def create_flagged_words(search_phrase, flagged_words, child_profile):
    for flagged_word in flagged_words:
        banned_word = BannedWord.objects.get(
            word=flagged_word.lower(),
            banned_for=child_profile,
        )
        flagged_word = FlaggedWord(
            flagged_search=search_phrase, flagged_word=banned_word
        )
        flagged_word.save()


def create_flagged_phrases(search_phrase, flagged_phrases):
    for flagged_phrase in flagged_phrases:
        flagged_word = FlaggedWord(
            flagged_search=search_phrase, flagged_word=flagged_phrase
        )
        flagged_word.save()


def is_within_time_range(current_time, start_time, end_time):
    """
    Check if the current time is within the specified time range.
    """
    if start_time < current_time < end_time:
        return True
    return False


def word_is_banned(word, banned_for):
    try:
        banned_word = BannedWord.banned.get(word=word.lower(), banned_for=banned_for)
        return True
    except BannedWord.DoesNotExist:
        return False


def has_banned_phrase(sentence, banned_for):
    # Query the database to check if the sentence contains any banned phrases
    banned_phrases = BannedWord.objects.values_list("word", flat=True).filter(
        banned_for=banned_for, banned_type=BannedType.PHRASE
    )

    for phrase in banned_phrases:
        if phrase.lower() in sentence.lower():
            return True

    return False


def get_banned_phrases(sentence, banned_for):
    # Query the database to check if the sentence contains any banned phrases
    banned_phrases = BannedWord.objects.values_list("word", flat=True).filter(
        banned_for=banned_for, banned_type=BannedType.PHRASE
    )
    phrases = list()

    for phrase in banned_phrases:
        if phrase.lower() in sentence.lower():
            phrases.append(phrase.lower())

    return phrases


def split_string(text):
    # Define a regular expression pattern to match commas, full stops, exclamation marks, or spaces
    pattern = r"[,\.\s!]+"

    # Use the re.split() function to split the text based on the pattern
    words = re.split(pattern, text)

    # Remove any empty strings from the result
    words = [word for word in words if word.strip()]

    return words


def filter_search_results(search_results, child_profile):
    filtered_results = []
    suspicious_results = []

    for result in search_results:
        # Split the title and snippet using split_string function
        title_words = split_string(result["title"])
        snippet_words = split_string(result["snippet"])

        # Check if the title or snippet contains any banned words by default
        title_has_banned_word = any(
            word_is_banned(word, banned_for=child_profile) for word in title_words
        )
        title_has_banned_phrase = has_banned_phrase(
            result["title"], banned_for=child_profile
        )

        snippet_has_banned_word = any(
            word_is_banned(word, banned_for=child_profile) for word in snippet_words
        )
        snippet_has_banned_phrase = has_banned_phrase(
            result["snippet"], banned_for=child_profile
        )

        # If none of them have banned words, add the result to filtered_results
        if not (
            title_has_banned_word
            or snippet_has_banned_word
            or snippet_has_banned_phrase
            or title_has_banned_phrase
        ):
            filtered_results.append(result)
        else:
            suspicious_results.append(result)

    return filtered_results, suspicious_results


def get_results(api_key, custom_search_engine_id, query, child_profile):
    search_results = list()

    # Make a request to the Google Custom Search API.
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={custom_search_engine_id}&q={query}&num=10"

    response = requests.get(url)

    # Parse and process the response (e.g., extract search results).
    try:
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

                filtered_search_results, suspicious_results = filter_search_results(
                    search_results, child_profile
                )
                return filtered_search_results, suspicious_results

            else:
                print("No search results found.")
                return None
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error{e}")
        logger.warning(f"Error: {e}")

