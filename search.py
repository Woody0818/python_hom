import requests
import json
from urllib.parse import quote
import time


def search(content: str):
    """
    Search using Wikipedia API as a fallback
    """
    try:
        # 使用更稳定的 Wikipedia API
        query = quote(content)
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}&utf8=1"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract relevant information
        search_results = data.get("query", {}).get("search", [])

        if search_results:
            # Format results
            result = f"## Search Results for: '{content}'\n\n"
            for i, item in enumerate(search_results[:3], 1):
                title = item.get("title", "")
                snippet = item.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", "")
                page_id = item.get("pageid", "")
                url = f"https://en.wikipedia.org/?curid={page_id}"

                result += f"### {i}. [{title}]({url})\n"
                result += f"{snippet}\n\n"

            return result
        else:
            return f"No search results found for: '{content}'"

    except Exception as e:
        print(f"Search error: {str(e)}")
        return (
            f"## Search Error\n\n"
            f"An error occurred while searching for '{content}':\n\n"
            f"Error details: {str(e)}\n\n"
            f"Please try again later or ask a different question."
        )