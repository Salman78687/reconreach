"""Gravatar — free person lookup from email MD5 hash. No API key required."""
import hashlib
import httpx


async def get_gravatar_profile(email: str) -> dict:
    """Look up a Gravatar profile from an email address.

    Returns name, avatar URL, bio/about, and URLs if the user has a Gravatar account.
    No API key required — just MD5 hash of lowercase, stripped email.
    """
    email_hash = hashlib.md5(email.lower().strip().encode()).hexdigest()
    url = f"https://www.gravatar.com/{email_hash}.json"

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                return {}

            data = resp.json()
            entry = data.get("entry", [{}])[0]

            name = None
            display_name = entry.get("displayName") or entry.get("preferredUsername")
            name_obj = entry.get("name", {})
            if name_obj:
                name = name_obj.get("formatted") or display_name
            else:
                name = display_name

            bio = entry.get("aboutMe") or None
            avatar_url = f"https://www.gravatar.com/avatar/{email_hash}?s=200"

            # Extract URLs
            urls = [u.get("value") for u in entry.get("urls", []) if u.get("value")]
            linkedin_url = next((u for u in urls if "linkedin.com" in u), None)
            github_url = next((u for u in urls if "github.com" in u), None)
            twitter_url = next((u for u in urls if "twitter.com" in u or "x.com" in u), None)

            result = {}
            if name:
                result["name"] = name
            if bio:
                result["bio"] = bio
            if avatar_url:
                result["avatar_url"] = avatar_url
            if linkedin_url:
                result["linkedin_url"] = linkedin_url
            if github_url:
                result["github_url"] = github_url
            if twitter_url:
                result["twitter_url"] = twitter_url

            return result

    except Exception:
        return {}
