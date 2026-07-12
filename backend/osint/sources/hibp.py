"""Have I Been Pwned (HIBP) — breach lookup for an email address.

API key required: https://haveibeenpwned.com/API/Key (~$3.50/month)
Set HIBP_API_KEY in backend/.env to enable.
"""
import httpx


async def check_breaches(email: str, api_key: str) -> dict:
    """Return a summary of data breaches the email appeared in.

    Returns dict with breach list and aggregated exposed data classes.
    Returns empty dict if email not found in any breach.
    """
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {
        "hibp-api-key": api_key,
        "User-Agent": "osint-cold-call/1.0",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers, params={"truncateResponse": "false"})

            if resp.status_code == 404:
                # Clean — not found in any breach
                return {"breached": False, "breach_count": 0, "breaches": []}

            if resp.status_code == 401:
                return {}  # Invalid key

            if resp.status_code == 429:
                return {}  # Rate limited

            if resp.status_code != 200:
                return {}

            breaches = resp.json()

            # Aggregate exposed data classes across all breaches
            all_data_classes: set[str] = set()
            breach_summaries = []
            for b in breaches:
                all_data_classes.update(b.get("DataClasses", []))
                breach_summaries.append({
                    "name": b.get("Name"),
                    "date": b.get("BreachDate"),
                    "data_classes": b.get("DataClasses", []),
                })

            return {
                "breached": True,
                "breach_count": len(breaches),
                "exposed_data": sorted(all_data_classes),
                "breaches": breach_summaries[:10],  # cap at 10 for storage
            }

    except Exception:
        return {}
