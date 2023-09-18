import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import *
from accounts.models import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings


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

        search_results = get_results(
            settings.GOOGLE_API_KEY,
            settings.CUSTOM_SEARCH_ENGINE_ID,
            search_query,
            no_of_results,
        )

        search_phrase = SearchPhrase(
            searched_by=child.childprofile,
            phrase=search_query,
            no_of_results=no_of_results,
        )
        search_phrase.save()

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
