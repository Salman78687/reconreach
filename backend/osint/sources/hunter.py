"""Hunter.io integration — company domain search + email enrichment."""
import httpx
from core.config import get_settings

BASE_URL = "https://api.hunter.io/v2"


async def get_company_from_domain(domain: str) -> dict:
    """Returns company info from Hunter.io domain search."""
    settings = get_settings()
    if not settings.hunter_api_key:
        return {}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{BASE_URL}/domain-search",
            params={"domain": domain, "api_key": settings.hunter_api_key},
        )
        if resp.status_code != 200:
            return {}

        data = resp.json().get("data", {})
        return {
            "company_name": data.get("organization"),
            "company_industry": data.get("industry"),
            "company_size": _map_size(data.get("company_size")),
            "company_website": f"https://{domain}",
            "linkedin_url": data.get("linkedin"),
            "twitter_url": data.get("twitter"),
        }


async def enrich_email(email: str) -> dict:
    """Returns person info from Hunter.io email enrichment."""
    settings = get_settings()
    if not settings.hunter_api_key:
        return {}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{BASE_URL}/email-enrichment",
            params={"email": email, "api_key": settings.hunter_api_key},
        )
        if resp.status_code != 200:
            return {}

        data = resp.json().get("data", {})
        return {
            "name": _full_name(data.get("first_name"), data.get("last_name")),
            "job_title": data.get("position"),
            "linkedin_url": data.get("linkedin"),
            "twitter_url": data.get("twitter"),
            "bio": data.get("bio"),
            "company_name": data.get("organization", {}).get("name") if data.get("organization") else None,
        }


def _full_name(first: str | None, last: str | None) -> str | None:
    parts = [p for p in [first, last] if p]
    return " ".join(parts) if parts else None


def _map_size(size_str: str | None) -> str | None:
    mapping = {
        "1-10": "1–10", "11-50": "11–50", "51-200": "51–200",
        "201-500": "201–500", "501-1000": "501–1,000", "1001-5000": "1,001–5,000",
        "5001-10000": "5,001–10,000", "10001+": "10,000+",
    }
    return mapping.get(size_str, size_str) if size_str else None
