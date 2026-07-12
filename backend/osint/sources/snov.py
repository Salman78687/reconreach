"""Snov.io — email verification and prospect lookup.

Free tier: 50 credits/month (no credit card needed for signup).
Get credentials at https://app.snov.io/api-setting
Set SNOV_CLIENT_ID and SNOV_CLIENT_SECRET in backend/.env.
"""
import httpx


async def _get_access_token(client_id: str, client_secret: str) -> str | None:
    """Obtain an OAuth2 access token from Snov.io."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://api.snov.io/v1/oauth/access_token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
            if resp.status_code != 200:
                return None
            return resp.json().get("access_token")
    except Exception:
        return None


async def enrich_email(email: str, client_id: str, client_secret: str) -> dict:
    """Verify email and look up profile information via Snov.io.

    Returns verification status, name, company, and job title if found.
    Consumes 1 credit per call on the free tier.
    """
    token = await _get_access_token(client_id, client_secret)
    if not token:
        return {}

    headers = {"Authorization": f"Bearer {token}"}
    result = {}

    try:
        async with httpx.AsyncClient(timeout=12) as client:
            # Step 1: Email verification (1 credit)
            verif_resp = await client.post(
                "https://api.snov.io/v1/email-verifier",
                headers=headers,
                json={"emails": [email]},
            )
            if verif_resp.status_code == 200:
                verif_data = verif_resp.json()
                emails_list = verif_data.get("emails", [])
                if emails_list:
                    entry = emails_list[0]
                    result["verification_status"] = entry.get("status")  # valid/invalid/unknown
                    result["smtp_valid"] = entry.get("smtpValid")
                    if entry.get("firstName") or entry.get("lastName"):
                        first = entry.get("firstName", "")
                        last = entry.get("lastName", "")
                        result["name"] = f"{first} {last}".strip()

            # Step 2: Profile lookup by email (1 credit)
            profile_resp = await client.post(
                "https://api.snov.io/v1/get-profile-by-email",
                headers=headers,
                json={"email": email},
            )
            if profile_resp.status_code == 200:
                pdata = profile_resp.json()
                if isinstance(pdata, dict) and pdata.get("success"):
                    person = pdata.get("data", {}) or {}
                    if person.get("name"):
                        result["name"] = result.get("name") or person["name"]
                    if person.get("currentJob"):
                        job = person["currentJob"][0] if isinstance(person["currentJob"], list) else person["currentJob"]
                        result["job_title"] = job.get("position")
                        result["company_name"] = job.get("organizationName")
                    if person.get("linkedinUrl"):
                        result["linkedin_url"] = person["linkedinUrl"]

    except Exception:
        pass

    return result
