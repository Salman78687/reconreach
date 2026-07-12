"""Enrichment pipeline for email leads."""
import asyncio
from email_validator import validate_email, EmailNotValidError

from core.config import get_settings
from models.enrichment import EnrichedProfile
from osint.sources import github, linkedin
from osint.sources.gravatar import get_gravatar_profile
from osint.sources.whois_lookup import get_whois_info
from osint.sources.emailrep import get_email_reputation
from osint.sources.hibp import check_breaches
from osint.sources.clearbit import enrich_person as clearbit_enrich
from osint.sources.snov import enrich_email as snov_enrich


def _source_entry(raw) -> dict:
    """Wrap a source result into {status, data} for raw_analysis storage."""
    if isinstance(raw, Exception):
        return {"status": "error", "data": str(raw)}
    if not raw:
        return {"status": "empty", "data": {}}
    return {"status": "success", "data": raw}


def _skipped(note: str) -> dict:
    return {"status": "skipped", "data": {}, "note": note}


async def enrich_email(email: str) -> EnrichedProfile:
    settings = get_settings()
    is_paid = settings.plan_tier == "paid"

    # Validate email
    try:
        valid = validate_email(email, check_deliverability=False)
        email = valid.normalized
    except EmailNotValidError:
        pass

    domain = email.split("@")[1]
    profile = EnrichedProfile(input_value=email, input_type="email")

    def safe(d) -> dict:
        return d if isinstance(d, dict) else {}

    # ── Wave 1: free sources always run ──────────────────────────────────────
    free_tasks = [
        get_gravatar_profile(email),
        get_whois_info(domain),
        get_email_reputation(email),
        github.find_github_profile(email),
        check_breaches(email, settings.hibp_api_key) if settings.hibp_api_key else asyncio.sleep(0),
        clearbit_enrich(email, settings.clearbit_api_key) if settings.clearbit_api_key else asyncio.sleep(0),
        snov_enrich(email, settings.snov_client_id, settings.snov_client_secret)
            if (settings.snov_client_id and settings.snov_client_secret) else asyncio.sleep(0),
    ]

    # ── Wave 1: paid sources (conditional) ───────────────────────────────────
    if is_paid:
        from osint.sources import hunter, apollo
        paid_tasks = [
            hunter.get_company_from_domain(domain),
            hunter.enrich_email(email),
            apollo.enrich_person(email),
        ]
    else:
        paid_tasks = []

    all_wave1 = await asyncio.gather(*free_tasks, *paid_tasks, return_exceptions=True)

    gravatar_data = all_wave1[0]
    whois_data = all_wave1[1]
    emailrep_data = all_wave1[2]
    github_data = all_wave1[3]
    hibp_data = all_wave1[4]
    clearbit_data = all_wave1[5]
    snov_data = all_wave1[6]

    if is_paid:
        company_from_domain = all_wave1[7]
        hunter_person = all_wave1[8]
        apollo_person = all_wave1[9]
    else:
        company_from_domain = None
        hunter_person = None
        apollo_person = None

    gv = safe(gravatar_data)
    wh = safe(whois_data)
    er = safe(emailrep_data)
    gh = safe(github_data)
    hb = safe(hibp_data)
    cb = safe(clearbit_data)
    sn = safe(snov_data)

    # Store raw results per source
    profile.raw_analysis["gravatar"] = _source_entry(gravatar_data)
    profile.raw_analysis["whois"] = _source_entry(whois_data)
    profile.raw_analysis["emailrep.io"] = _source_entry(emailrep_data)
    profile.raw_analysis["github"] = _source_entry(github_data)

    if settings.hibp_api_key:
        profile.raw_analysis["hibp"] = _source_entry(hibp_data)
    else:
        profile.raw_analysis["hibp"] = _skipped("HIBP_API_KEY not configured")

    if settings.clearbit_api_key:
        profile.raw_analysis["clearbit"] = _source_entry(clearbit_data)
    else:
        profile.raw_analysis["clearbit"] = _skipped("CLEARBIT_API_KEY not configured")

    if settings.snov_client_id and settings.snov_client_secret:
        profile.raw_analysis["snov.io"] = _source_entry(snov_data)
    else:
        profile.raw_analysis["snov.io"] = _skipped("SNOV_CLIENT_ID/SECRET not configured")

    if is_paid:
        profile.raw_analysis["hunter.io/domain"] = _source_entry(company_from_domain)
        profile.raw_analysis["hunter.io/email"] = _source_entry(hunter_person)
        profile.raw_analysis["apollo.io"] = _source_entry(apollo_person)
    else:
        profile.raw_analysis["hunter.io/domain"] = _skipped("paid plan only")
        profile.raw_analysis["hunter.io/email"] = _skipped("paid plan only")
        profile.raw_analysis["apollo.io"] = _skipped("paid plan only")

    sources_used = []

    # Merge free source results
    if gv:
        sources_used.append("gravatar")
        profile.name = profile.name or gv.get("name")
        profile.bio = profile.bio or gv.get("bio")
        profile.linkedin_url = profile.linkedin_url or gv.get("linkedin_url")
        profile.github_url = profile.github_url or gv.get("github_url")
        profile.twitter_url = profile.twitter_url or gv.get("twitter_url")

    if wh:
        sources_used.append("whois")
        profile.company_name = profile.company_name or wh.get("org")

    if er:
        sources_used.append("emailrep.io")

    if gh:
        sources_used.append("github")
        profile.github_url = profile.github_url or gh.get("github_url")
        profile.name = profile.name or gh.get("name")
        profile.bio = profile.bio or gh.get("bio")
        if gh.get("interests"):
            profile.interests = gh["interests"]

    if hb and hb.get("breach_count", 0) > 0:
        sources_used.append("hibp")

    if cb:
        sources_used.append("clearbit")
        profile.name = profile.name or cb.get("name")
        profile.job_title = profile.job_title or cb.get("job_title")
        profile.bio = profile.bio or cb.get("bio")
        profile.linkedin_url = profile.linkedin_url or cb.get("linkedin_url")
        profile.twitter_url = profile.twitter_url or cb.get("twitter_url")
        profile.github_url = profile.github_url or cb.get("github_url")
        profile.company_name = profile.company_name or cb.get("company_name")
        profile.company_industry = profile.company_industry or cb.get("company_industry")
        profile.company_size = profile.company_size or cb.get("company_size")
        profile.company_website = profile.company_website or cb.get("company_website")
        profile.company_description = profile.company_description or cb.get("company_description")

    if sn:
        sources_used.append("snov.io")
        profile.name = profile.name or sn.get("name")
        profile.job_title = profile.job_title or sn.get("job_title")
        profile.company_name = profile.company_name or sn.get("company_name")
        profile.linkedin_url = profile.linkedin_url or sn.get("linkedin_url")

    # Merge paid source results (when available)
    if is_paid:
        company_info = safe(company_from_domain)
        hp = safe(hunter_person)
        ap = safe(apollo_person)

        if company_info:
            sources_used.append("hunter.io/domain")
            profile.company_name = profile.company_name or company_info.get("company_name")
            profile.company_industry = profile.company_industry or company_info.get("company_industry")
            profile.company_size = profile.company_size or company_info.get("company_size")
            profile.company_website = profile.company_website or company_info.get("company_website")

        if hp:
            sources_used.append("hunter.io/email")
            profile.name = profile.name or hp.get("name")
            profile.job_title = profile.job_title or hp.get("job_title")
            profile.linkedin_url = profile.linkedin_url or hp.get("linkedin_url")
            profile.twitter_url = profile.twitter_url or hp.get("twitter_url")
            profile.bio = profile.bio or hp.get("bio")
            profile.company_name = profile.company_name or hp.get("company_name")

        if ap:
            sources_used.append("apollo.io")
            profile.name = profile.name or ap.get("name")
            profile.job_title = profile.job_title or ap.get("job_title")
            profile.linkedin_url = profile.linkedin_url or ap.get("linkedin_url")
            profile.twitter_url = profile.twitter_url or ap.get("twitter_url")
            profile.company_name = profile.company_name or ap.get("company_name")
            profile.company_industry = profile.company_industry or ap.get("company_industry")
            profile.company_size = profile.company_size or ap.get("company_size")
            profile.company_website = profile.company_website or ap.get("company_website")
            profile.company_description = ap.get("company_description")

    # ── Wave 2: dependent steps (use Wave 1 results) ─────────────────────────
    tasks = []

    if profile.name or profile.linkedin_url:
        tasks.append(
            linkedin.get_linkedin_profile(profile.name, profile.company_name, profile.linkedin_url)
        )
    else:
        tasks.append(asyncio.sleep(0))

    if is_paid and profile.name:
        from osint.sources import google_search
        tasks.append(google_search.get_recent_news(profile.name, profile.company_name))
        tasks.append(google_search.get_company_news(profile.company_name) if profile.company_name else asyncio.sleep(0))
    else:
        tasks.append(asyncio.sleep(0))
        tasks.append(asyncio.sleep(0))

    dep_results = await asyncio.gather(*tasks, return_exceptions=True)
    li_data, person_news, company_news = dep_results

    li_data = safe(li_data) if isinstance(li_data, dict) else {}
    profile.raw_analysis["linkedin"] = _source_entry(li_data if li_data else {})
    if li_data.get("linkedin_url"):
        sources_used.append("linkedin")
        profile.linkedin_url = profile.linkedin_url or li_data.get("linkedin_url")
        profile.bio = profile.bio or li_data.get("bio")

    if is_paid:
        profile.raw_analysis["google_news/person"] = _source_entry(
            person_news if not isinstance(person_news, Exception) else person_news
        )
        profile.raw_analysis["google_news/company"] = _source_entry(
            company_news if not isinstance(company_news, Exception) else company_news
        )
    else:
        profile.raw_analysis["google_news/person"] = _skipped("paid plan only")
        profile.raw_analysis["google_news/company"] = _skipped("paid plan only")

    news_headlines = []
    if is_paid:
        if isinstance(person_news, list):
            news_headlines.extend(person_news)
            if person_news:
                sources_used.append("google_news/person")
        if isinstance(company_news, list):
            news_headlines.extend(company_news)
            if company_news:
                sources_used.append("google_news/company")

    profile.recent_news = list(dict.fromkeys(news_headlines))[:5]

    # ── Twitter (paid only, needs twitter_url from Wave 1) ───────────────────
    if is_paid and profile.twitter_url:
        from osint.sources.twitter import extract_username_from_url, get_recent_tweets
        handle = extract_username_from_url(profile.twitter_url)
        if handle:
            tweets = await get_recent_tweets(handle, max_results=10)
            profile.raw_analysis["twitter/x"] = _source_entry(tweets or [])
            if tweets:
                profile.recent_posts = tweets[:5]
                sources_used.append("twitter/x")
        else:
            profile.raw_analysis["twitter/x"] = {"status": "empty", "data": [], "note": "could not parse handle from URL"}
    elif is_paid:
        profile.raw_analysis["twitter/x"] = {"status": "skipped", "data": [], "note": "no twitter URL found"}
    else:
        profile.raw_analysis["twitter/x"] = _skipped("paid plan only")

    profile.enrichment_sources = list(dict.fromkeys(sources_used))
    return profile
