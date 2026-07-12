from llm.client import LLMClient
from llm.prompts import SYSTEM_EMAIL, build_recipient_summary, build_seller_summary


async def generate_cold_email(client: LLMClient, seller: dict, recipient: dict) -> str:
    user_prompt = f"""Generate a cold email for the following:

SELLER CONTEXT:
{build_seller_summary(seller)}

RECIPIENT CONTEXT:
{build_recipient_summary(recipient)}

Write the email body only (no subject line). Under 150 words."""

    return await client.complete(system=SYSTEM_EMAIL, user=user_prompt)
