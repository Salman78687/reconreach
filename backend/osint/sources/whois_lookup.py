"""WHOIS — free domain lookup using python-whois. No API key required."""
import asyncio


async def get_whois_info(domain: str) -> dict:
    """Look up WHOIS data for a domain.

    Returns organization name, registrar, creation date, country, and emails.
    Uses python-whois library which is free and offline (queries public WHOIS servers).
    """
    try:
        import whois as python_whois

        # python-whois is synchronous — run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, python_whois.whois, domain)

        if not data:
            return {}

        result = {}

        # Organization name
        org = data.get("org") or data.get("organization") or data.get("registrant_organization")
        if org:
            result["org"] = str(org) if not isinstance(org, list) else org[0]

        # Registrar
        registrar = data.get("registrar")
        if registrar:
            result["registrar"] = str(registrar) if not isinstance(registrar, list) else registrar[0]

        # Country
        country = data.get("country") or data.get("registrant_country")
        if country:
            result["country"] = str(country) if not isinstance(country, list) else country[0]

        # Creation date
        creation_date = data.get("creation_date")
        if creation_date:
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            result["creation_date"] = str(creation_date)[:10]  # just the date portion

        # Registrant emails (sometimes public)
        emails = data.get("emails")
        if emails:
            if isinstance(emails, str):
                emails = [emails]
            result["registrant_emails"] = emails[:3]

        return result

    except Exception:
        return {}
