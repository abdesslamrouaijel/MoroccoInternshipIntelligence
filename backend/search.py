from dataclasses import dataclass
from urllib.parse import quote_plus, urlparse

import requests
from bs4 import BeautifulSoup


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str


class PublicWebSearch:
    """Fetches public DuckDuckGo HTML results without login or anti-bot circumvention."""

    endpoint = "https://html.duckduckgo.com/html/"

    def search(self, query, limit=20, timeout=15):
        response = requests.get(
            self.endpoint,
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (compatible; MoroccoInternshipIntelligence/1.0)"},
            timeout=timeout,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for item in soup.select(".result"):
            anchor = item.select_one(".result__a")
            snippet_node = item.select_one(".result__snippet")
            if not anchor or not anchor.get("href"):
                continue
            url = anchor["href"]
            domain = urlparse(url).netloc.removeprefix("www.")
            results.append(SearchResult(
                title=anchor.get_text(" ", strip=True),
                url=url,
                snippet=snippet_node.get_text(" ", strip=True) if snippet_node else "",
                source=domain,
            ))
            if len(results) >= limit:
                break
        return results


def search_url(query):
    return PublicWebSearch.endpoint + "?q=" + quote_plus(query)
