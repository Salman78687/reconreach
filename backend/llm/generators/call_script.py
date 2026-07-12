from llm.client import LLMClient
from llm.prompts import SYSTEM_CALL_SCRIPT, build_recipient_summary, build_seller_summary


async def generate_call_script(client: LLMClient, seller: dict, recipient: dict) -> str:
    user_prompt = f"""Generate a cold call script for the following:

SELLER CONTEXT:
{build_seller_summary(seller)}

RECIPIENT CONTEXT:
{build_recipient_summary(recipient)}

Format it with the 5-step structure. Under 300 words."""

    return await client.complete(system=SYSTEM_CALL_SCRIPT, user=user_prompt)
