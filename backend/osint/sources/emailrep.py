"""EmailRep.io — free email reputation lookup. No API key required for basic use."""
import httpx


async def get_email_reputation(email: str) -> dict:
    """Look up email reputation from emailrep.io.

    Returns reputation score, breach flags, domain info, and other signals.
    Free tier requires no API key but is rate-limited to ~100 req/day.
    """
    url = f"https://emailrep.io/{email}"

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                url,
                headers={
                    "User-Agent": "osint-cold-call/1.0",
                    "Accept": "application/json",
                },
            )
            if resp.status_code != 200:
                return {}

            data = resp.json()
            if not data:
                return {}

            result = {}

            # Reputation
            reputation = data.get("reputation")
            if reputation:
                result["reputation"] = reputation  # "high", "medium", "low", "none"

            # Risk signals
            result["suspicious"] = data.get("suspicious", False)

            details = data.get("details", {})
            if details:
                # Breach info
                if details.get("data_breach"):
                    result["data_breach"] = True
                    result["breach_count"] = details.get("breach_count", 0)

                # Profile presence signals
                if details.get("profiles"):
                    result["profiles"] = details["profiles"]  # e.g. ["linkedin", "github"]

                # Domain info
                if details.get("domain_reputation"):
                    result["domain_reputation"] = details["domain_reputation"]

                if details.get("days_since_domain_creation"):
                    result["domain_age_days"] = details["days_since_domain_creation"]

                # Disposable / free email flag
                if details.get("free_provider"):
                    result["free_provider"] = True
                if details.get("disposable"):
                    result["disposable"] = True

                # Deliverability
                if details.get("deliverability"):
                    result["deliverability"] = details["deliverability"]

            return result

    except Exception:
        return {}
