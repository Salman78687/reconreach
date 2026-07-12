from llm.client import LLMClient
from llm.prompts import SYSTEM_LINKEDIN, build_recipient_summary, build_seller_summary


async def generate_linkedin_msg(client: LLMClient, seller: dict, recipient: dict) -> str:
    user_prompt = f"""Generate a LinkedIn connection message for the following:

SELLER CONTEXT:
{build_seller_summary(seller)}

RECIPIENT CONTEXT:
{build_recipient_summary(recipient)}

Under 80 words. No emojis."""

    return await client.complete(system=SYSTEM_LINKEDIN, user=user_prompt)
