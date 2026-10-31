import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
load_dotenv()

tavily=TavilyClient( api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic.
    Returns titles, URLs and short snippets."""
    results = tavily.search(query=query, max_results=5)

    out = []
    for r in results["results"]:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )

    return "\n----\n".join(out)


import requests
from bs4 import BeautifulSoup


@tool
def scrape_url(url: str) -> str:
    """Scrape and return the readable text content of a webpage given its URL.
    Use this to get deeper details from a specific page."""
    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        # removing the junk we don't want the LLM to read
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return text[:3000]

    except Exception as e:
        return f"Could not scrape {url}: {e}"