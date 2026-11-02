from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OSINT sources — Paid tier
    hunter_api_key: str = ""
    apollo_api_key: str = ""
    github_token: str = ""
    google_cse_api_key: str = ""
    google_cse_id: str = ""
    twitter_bearer_token: str = ""

    # Free-tier optional keys (sign up free, no payment needed for basic use)
    hibp_api_key: str = ""           # haveibeenpwned.com — paid API subscription
    clearbit_api_key: str = ""       # clearbit.com — free trial available
    snov_client_id: str = ""         # snov.io — 50 free credits/mo
    snov_client_secret: str = ""

    # Plan tier: "free" uses only zero-cost tools; "paid" adds API-key sources
    plan_tier: str = "free"

    # Self-hosted LLM (OpenAI-compatible API)
    llm_api_base: str = "http://localhost:11434/v1"  # Ollama's default address
    llm_api_key: str = "EMPTY"
    llm_model: str = "llama3.1"

    # App
    # Comma-separated origins allowed to call the API (the frontend's URL)
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    database_url: str = "sqlite:///./osint_cold_call.db"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
