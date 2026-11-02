"""LinkedIn public profile scraping via Google dork + BeautifulSoup."""
import httpx
from bs4 import BeautifulSoup
from osint.sources.google_search import find_linkedin_url


async def get_linkedin_profile(name: str | None, company: str | None, linkedin_url: str | None = None) -> dict:
    """
    Attempt to scrape public LinkedIn profile info.
    LinkedIn blocks most scraping — this relies on Google cache snippets.
    Returns what it can; empty dict on failure.
    """
    if not linkedin_url and name:
        linkedin_url = await find_linkedin_url(name, company)

    if not linkedin_url:
        return {}

    # Try to fetch the public LinkedIn page
    # Note: LinkedIn aggressively blocks scrapers. We extract what Google snippet gave us.
    # For a production setup, use a LinkedIn scraping service (e.g. Proxycurl).
    headers = {
        "User-Agent": "osint-outreach-platform/1.0 (+https://github.com/Salman78687/osint-outreach-platform)",
    }

    try:
        async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
            resp = await client.get(linkedin_url)
            if resp.status_code != 200:
                return {"linkedin_url": linkedin_url}

            soup = BeautifulSoup(resp.text, "html.parser")

            # Extract title tag which often has "Name - Title at Company | LinkedIn"
            title = soup.find("title")
            title_text = title.get_text() if title else ""

            # Extract meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            bio = meta_desc.get("content") if meta_desc else None

            return {
                "linkedin_url": linkedin_url,
                "bio": bio,
                "_title_hint": title_text,
            }
    except Exception:
        return {"linkedin_url": linkedin_url}
