"""Google Custom Search API — news lookup and LinkedIn URL discovery."""
import httpx
from core.config import get_settings

BASE_URL = "https://www.googleapis.com/customsearch/v1"


async def search(query: str, num: int = 5) -> list[dict]:
    """Returns list of {title, link, snippet} dicts."""
    settings = get_settings()
    if not settings.google_cse_api_key or not settings.google_cse_id:
        return []

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            BASE_URL,
            params={
                "key": settings.google_cse_api_key,
                "cx": settings.google_cse_id,
                "q": query,
                "num": min(num, 10),
            },
        )
        if resp.status_code != 200:
            return []

        items = resp.json().get("items", [])
        return [
            {"title": i.get("title"), "link": i.get("link"), "snippet": i.get("snippet")}
            for i in items
        ]


async def find_linkedin_url(name: str, company: str | None = None) -> str | None:
    """Use Google to find a LinkedIn profile URL."""
    query = f'site:linkedin.com/in "{name}"'
    if company:
        query += f' "{company}"'

    results = await search(query, num=3)
    for r in results:
        if "linkedin.com/in/" in (r.get("link") or ""):
            return r["link"]
    return None


async def get_recent_news(name: str, company: str | None = None) -> list[str]:
    """Get recent news headlines about a person or their company."""
    query = f'"{name}"'
    if company:
        query += f' "{company}"'

    results = await search(query, num=5)
    headlines = []
    for r in results:
        snippet = r.get("snippet") or r.get("title") or ""
        if snippet:
            headlines.append(snippet)
    return headlines[:5]


async def get_company_news(company_name: str) -> list[str]:
    query = f'"{company_name}" news'
    results = await search(query, num=5)
    return [r.get("title") or r.get("snippet") for r in results if r.get("title")][:5]
