import requests
from bs4 import BeautifulSoup

def fetch(url: str):
    """
    Fetches the content of a URL, extracts text from all <p> tags,
    and formats it into a summarization prompt.

    Args:
        url: The URL of the webpage to summarize.

    Returns:
        A formatted string prompt for the language model, or an error message.
    """
    try:
        response = requests.get(url, timeout=10)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # The document specifies using BeautifulSoup to parse the HTML. [cite: 193]
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <p> tags and extract their text, as required. [cite: 172, 189]
        paragraphs = soup.find_all('p')
        processed_results = "\n".join([p.get_text() for p in paragraphs])

        if not processed_results:
            return f"No paragraph text found on {url}."

        # Format the extracted text into a prompt for summarization. [cite: 182]
        question = f"Act as a summarizer. Please summarize {url}. The following is the content:\n\n{processed_results}"
        return question

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}"
    except Exception as e:
        return f"An error occurred during fetching or parsing: {e}"


if __name__ == "__main__":
    # Example usage with the URL specified in the document. [cite: 172, 189]
    summary_prompt = fetch("https://dev.qweather.com/en/help")
    print(summary_prompt)