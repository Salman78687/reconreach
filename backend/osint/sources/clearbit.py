"""Clearbit — combined person + company enrichment from email.

API key required: https://dashboard.clearbit.com/
Set CLEARBIT_API_KEY in backend/.env to enable.
Free trial available; paid plans from $99/mo for bulk use.
"""
import httpx


async def enrich_person(email: str, api_key: str) -> dict:
    """Look up a person profile + company info from an email via Clearbit.

    Returns person name, title, bio, social handles, and company details.
    """
    url = "https://person.clearbit.com/v2/combined/find"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers, params={"email": email})

            if resp.status_code in (401, 403):
                return {}  # Invalid or expired key

            if resp.status_code == 404:
                return {}  # Not found

            if resp.status_code == 402:
                return {}  # Payment required / quota exceeded

            if resp.status_code == 202:
                # Clearbit is processing asynchronously — data not ready yet
                return {}

            if resp.status_code != 200:
                return {}

            data = resp.json()
            result = {}

            person = data.get("person") or {}
            company = data.get("company") or {}

            # Person fields
            name_obj = person.get("name", {}) or {}
            full_name = name_obj.get("fullName")
            if full_name:
                result["name"] = full_name

            employment = person.get("employment", {}) or {}
            title = employment.get("title")
            if title:
                result["job_title"] = title

            emp_name = employment.get("name")
            if emp_name:
                result["company_name"] = emp_name

            bio = person.get("bio")
            if bio:
                result["bio"] = bio

            # Social handles
            linkedin = (person.get("linkedin", {}) or {}).get("handle")
            if linkedin:
                result["linkedin_url"] = f"https://linkedin.com/in/{linkedin}"

            twitter = (person.get("twitter", {}) or {}).get("handle")
            if twitter:
                result["twitter_url"] = f"https://twitter.com/{twitter}"

            github = (person.get("github", {}) or {}).get("handle")
            if github:
                result["github_url"] = f"https://github.com/{github}"

            # Company fields
            if company:
                if company.get("name"):
                    result["company_name"] = result.get("company_name") or company["name"]
                if company.get("category", {}) and company["category"].get("industry"):
                    result["company_industry"] = company["category"]["industry"]
                metrics = company.get("metrics", {}) or {}
                if metrics.get("employeesRange"):
                    result["company_size"] = metrics["employeesRange"]
                if company.get("domain"):
                    result["company_website"] = f"https://{company['domain']}"
                if company.get("description"):
                    result["company_description"] = company["description"]

            return result

    except Exception:
        return {}
