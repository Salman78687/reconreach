"""LLM client using self-hosted OpenAI-compatible API."""
from openai import AsyncOpenAI
from core.config import get_settings


class LLMClient:
    def __init__(self):
        s = get_settings()
        self._client = AsyncOpenAI(api_key=s.llm_api_key, base_url=s.llm_api_base)
        self.model = s.llm_model

    async def complete(self, system: str, user: str) -> str:
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
