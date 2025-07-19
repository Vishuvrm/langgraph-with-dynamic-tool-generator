import requests
from bs4 import BeautifulSoup
from langchain.tools import tool

@tool
def search_tool(search_query: str) -> list[dict]:
    """
    Performs web search using Bing and returns the top results.

    Args:
        search_query (str): A string representing the web search query.

    Returns:
        list[dict]: A list of search results containing title, href, and body.
    """
    from langchain_community.utilities import BingSearchAPIWrapper
    search = BingSearchAPIWrapper()
    search_results = search.results(search_query, 20)
    return "\n------\n".join(["Title: "+result['title'] + "\n" + "Link: " + result['link'] + "\nDescription: " + result['snippet'] for result in search_results])

@tool
def deep_dive_tool(url: str) -> str:
    """
    Fetches the text content of a webpage given its URL.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        str: The text content of the webpage.
    """        
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(strip=True)
    return "Failed to fetch content"

@tool
def get_raw_html_tool(url: str) -> str:
    """
    Fetches the raw HTML content of a webpage given its URL.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        str: The raw HTML content of the webpage.
    """
    response = requests.get(url)
    return response.text