"""GitHub API — find a developer's profile from their email (free API)."""
import httpx
from core.config import get_settings


async def find_github_profile(email: str) -> dict:
    settings = get_settings()
    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    async with httpx.AsyncClient(timeout=10, headers=headers) as client:
        # Search commits by email — most reliable way to find GitHub user from email
        resp = await client.get(
            "https://api.github.com/search/commits",
            params={"q": f"author-email:{email}", "per_page": 1},
            headers={**headers, "Accept": "application/vnd.github.cloak-preview+json"},
        )
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                login = items[0]["author"]["login"]
                return await _get_user_profile(client, login, headers)

        # Fallback: search users by email directly
        resp2 = await client.get(
            "https://api.github.com/search/users",
            params={"q": f"{email} in:email", "per_page": 1},
        )
        if resp2.status_code == 200:
            items = resp2.json().get("items", [])
            if items:
                login = items[0]["login"]
                return await _get_user_profile(client, login, headers)

    return {}


async def _get_user_profile(client: httpx.AsyncClient, login: str, headers: dict) -> dict:
    resp = await client.get(f"https://api.github.com/users/{login}", headers=headers)
    if resp.status_code != 200:
        return {}

    user = resp.json()
    interests: list[str] = []

    # Get their top repos to infer interests
    repos_resp = await client.get(
        f"https://api.github.com/users/{login}/repos",
        params={"sort": "stars", "per_page": 5},
        headers=headers,
    )
    if repos_resp.status_code == 200:
        repos = repos_resp.json()
        for repo in repos:
            if repo.get("language"):
                interests.append(repo["language"])
            if repo.get("topics"):
                interests.extend(repo["topics"])

    interests = list(dict.fromkeys(interests))[:8]  # deduplicate, keep order

    return {
        "github_url": user.get("html_url"),
        "name": user.get("name"),
        "bio": user.get("bio"),
        "company_name": (user.get("company") or "").lstrip("@") or None,
        "interests": interests,
    }
