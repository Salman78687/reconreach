"""Twitter/X Basic API — fetch recent tweets for a username."""
import httpx
from core.config import get_settings

BASE_URL = "https://api.twitter.com/2"


async def get_recent_tweets(username: str, max_results: int = 10) -> list[str]:
    """Returns list of recent tweet texts for a Twitter/X username."""
    settings = get_settings()
    if not settings.twitter_bearer_token:
        return []

    headers = {"Authorization": f"Bearer {settings.twitter_bearer_token}"}

    async with httpx.AsyncClient(timeout=10, headers=headers) as client:
        # First look up user ID
        user_resp = await client.get(
            f"{BASE_URL}/users/by/username/{username}",
        )
        if user_resp.status_code != 200:
            return []

        user_id = user_resp.json().get("data", {}).get("id")
        if not user_id:
            return []

        # Get recent tweets
        tweets_resp = await client.get(
            f"{BASE_URL}/users/{user_id}/tweets",
            params={
                "max_results": min(max_results, 100),
                "tweet.fields": "text,created_at",
                "exclude": "retweets,replies",
            },
        )
        if tweets_resp.status_code != 200:
            return []

        tweets = tweets_resp.json().get("data", [])
        return [t["text"] for t in tweets if t.get("text")]


def extract_username_from_url(url: str | None) -> str | None:
    """Extract @handle from a Twitter/X URL."""
    if not url:
        return None
    # Handle formats: twitter.com/handle, x.com/handle
    for prefix in ["twitter.com/", "x.com/"]:
        if prefix in url:
            handle = url.split(prefix)[-1].rstrip("/").split("?")[0]
            return handle if handle else None
    return None
