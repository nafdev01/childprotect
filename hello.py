
import requests

# Replace 'YOUR_API_KEY' with the API key you obtained from the Google Cloud Console.
api_key = 'AIzaSyDRpojxZNjaQm_vi0-6ZK04aE6N0uMqZpE'

# Define the search query and custom search engine ID.
query = 'How to eat oysters'
custom_search_engine_id = '54d9a04ccf98c4dcb'

# Specify the number of results you want to retrieve (maximum is 10).
num_results = 10

# Make a request to the Google Custom Search API.
url = f'https://www.googleapis.com/customsearch/v1?key={api_key}&cx={custom_search_engine_id}&q={query}&num={num_results}'

response = requests.get(url)

# Parse and process the response (e.g., extract search results).
if response.status_code == 200:
    data = response.json()
    
    # Check if there are search results
    if 'items' in data:
        # Iterate through the search results and print them
        for index, item in enumerate(data['items'], start=1):
            print(f"Result {index}:")
            print(f"Title: {item['title']}")
            print(f"Link: {item['link']}")
            print(f"Snippet: {item['snippet']}")
            print("\n")
    else:
        print("No search results found.")
else:
    print(f"Error: {response.status_code}")
