def build_recipient_summary(recipient: dict) -> str:
    """Convert enriched recipient data into a readable summary for the LLM prompt."""
    parts = []

    if recipient.get("name"):
        line = f"Name: {recipient['name']}"
        if recipient.get("job_title"):
            line += f", {recipient['job_title']}"
        if recipient.get("company_name"):
            line += f" at {recipient['company_name']}"
        parts.append(line)

    if recipient.get("company_industry"):
        parts.append(f"Industry: {recipient['company_industry']}")

    if recipient.get("bio"):
        parts.append(f"Bio: {recipient['bio']}")

    if recipient.get("recent_posts"):
        posts = recipient["recent_posts"][:3]
        parts.append("Recent activity / posts:")
        for p in posts:
            parts.append(f"  - {p}")

    if recipient.get("interests"):
        parts.append(f"Interests: {', '.join(recipient['interests'][:5])}")

    if recipient.get("recent_news"):
        news = recipient["recent_news"][:2]
        parts.append("Recent news about them / their company:")
        for n in news:
            parts.append(f"  - {n}")

    return "\n".join(parts) if parts else "No enriched data available."


def build_seller_summary(seller: dict) -> str:
    parts = [
        f"Product/Service: {seller['product_name']}",
        f"Description: {seller['product_description']}",
        f"Pain point addressed: {seller['target_pain_point']}",
    ]
    if seller.get("key_value_props"):
        parts.append("Key value propositions:")
        for v in seller["key_value_props"]:
            parts.append(f"  - {v}")
    return "\n".join(parts)


SYSTEM_EMAIL = """You are an expert cold email copywriter.
Your goal is to write a short, highly personalized cold email (under 150 words) that hooks the recipient.
Rules:
- Open with a specific, genuine observation about the recipient (from their activity, interests, or recent news)
- One short paragraph connecting their context to the seller's value prop
- A soft, low-friction CTA (e.g., "Worth a 15-min chat?")
- No fluff, no generic openers like "I hope this finds you well"
- No subject line — just the body
- Write in first-person as the sender"""

SYSTEM_CALL_SCRIPT = """You are an expert cold call coach.
Write a structured cold call script (under 300 words) that is highly personalized.
Format:
1. Opening (5 sec) — pattern interrupt, reference something specific about them
2. Permission ask (5 sec) — "I'll be quick..."
3. Bridge (15 sec) — connect their context to the seller's value
4. Qualifying question (10 sec)
5. CTA — schedule a call
Keep it conversational, not salesy."""

SYSTEM_LINKEDIN = """You are an expert LinkedIn outreach specialist.
Write a short LinkedIn connection message (under 80 words) that is personalized and not salesy.
- Start with a specific observation about their work or content
- One sentence on why you're reaching out
- End with a simple, no-pressure ask
No emojis, no "I came across your profile", keep it human."""
