"""Apollo.io integration — person enrichment via email."""
import httpx
from core.config import get_settings

BASE_URL = "https://api.apollo.io/v1"


async def enrich_person(email: str) -> dict:
    settings = get_settings()
    if not settings.apollo_api_key:
        return {}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{BASE_URL}/people/match",
            headers={"Content-Type": "application/json", "Cache-Control": "no-cache"},
            json={"api_key": settings.apollo_api_key, "email": email},
        )
        if resp.status_code != 200:
            return {}

        person = resp.json().get("person", {})
        if not person:
            return {}

        org = person.get("organization", {}) or {}
        return {
            "name": person.get("name"),
            "job_title": person.get("title"),
            "linkedin_url": person.get("linkedin_url"),
            "twitter_url": person.get("twitter_url"),
            "city": person.get("city"),
            "country": person.get("country"),
            "company_name": org.get("name"),
            "company_industry": org.get("industry"),
            "company_size": _format_size(org.get("estimated_num_employees")),
            "company_website": org.get("website_url"),
            "company_description": org.get("short_description"),
        }


def _format_size(n: int | None) -> str | None:
    if n is None:
        return None
    if n < 10:
        return "1–10"
    if n < 50:
        return "11–50"
    if n < 200:
        return "51–200"
    if n < 500:
        return "201–500"
    if n < 1000:
        return "501–1,000"
    if n < 5000:
        return "1,001–5,000"
    return "5,000+"
