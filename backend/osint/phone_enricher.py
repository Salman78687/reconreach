"""Enrichment pipeline for phone number leads."""
from models.enrichment import EnrichedProfile
from osint.sources.phoneinfoga import parse_phone, run_phoneinfoga
from osint.sources.google_search import search


async def enrich_phone(phone: str) -> EnrichedProfile:
    profile = EnrichedProfile(input_value=phone, input_type="phone")
    sources_used = []

    # Step 1: Parse with phonenumbers lib (always free)
    parsed = parse_phone(phone)
    profile.raw_analysis["phonenumbers"] = {
        "status": "success" if parsed.get("is_valid") else "invalid",
        "data": parsed,
    }
    if parsed.get("is_valid"):
        sources_used.append("phonenumbers")
        carrier = parsed.get("carrier")
        country = parsed.get("country")
        line_type = parsed.get("line_type")
        profile.company_description = f"Carrier: {carrier or 'unknown'} | Country: {country or 'unknown'} | Type: {line_type or 'unknown'}"

    # Step 2: PhoneInfoga CLI (if installed)
    phoneinfoga_data = await run_phoneinfoga(parsed.get("formatted", phone))
    profile.raw_analysis["phoneinfoga"] = {
        "status": "success" if phoneinfoga_data else "empty",
        "data": phoneinfoga_data,
    }
    if phoneinfoga_data:
        sources_used.append("phoneinfoga")

    # Step 3: Google reverse lookup
    google_results = await search(f'"{phone}"', num=5)
    profile.raw_analysis["google_search"] = {
        "status": "success" if google_results else "empty",
        "data": google_results,
    }
    if google_results:
        sources_used.append("google_search")
        for result in google_results:
            snippet = result.get("snippet") or ""
            title = result.get("title") or ""
            combined = f"{title}: {snippet}" if title else snippet
            if combined:
                profile.recent_news.append(combined)
        profile.recent_news = profile.recent_news[:3]

        for result in google_results:
            link = result.get("link") or ""
            if "linkedin.com/in/" in link:
                profile.linkedin_url = link
                sources_used.append("linkedin_found")
                break

    # Step 4: LinkedIn scrape if URL found
    if profile.linkedin_url:
        from osint.sources.linkedin import get_linkedin_profile
        li_data = await get_linkedin_profile(None, None, profile.linkedin_url)
        profile.raw_analysis["linkedin"] = {
            "status": "success" if li_data else "empty",
            "data": li_data,
        }
        if li_data:
            profile.bio = li_data.get("bio")
    else:
        profile.raw_analysis["linkedin"] = {"status": "skipped", "data": {}, "note": "no LinkedIn URL found"}

    profile.enrichment_sources = list(dict.fromkeys(sources_used))
    return profile
