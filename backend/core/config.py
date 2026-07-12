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
    numverify_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""

    # Free-tier optional keys (sign up free, no payment needed for basic use)
    hibp_api_key: str = ""           # haveibeenpwned.com — ~$3.50/mo for API
    clearbit_api_key: str = ""       # clearbit.com — free trial available
    snov_client_id: str = ""         # snov.io — 50 free credits/mo
    snov_client_secret: str = ""

    # Plan tier: "free" uses only zero-cost tools; "paid" adds API-key sources
    plan_tier: str = "free"

    # Self-hosted LLM (OpenAI-compatible API)
    llm_api_base: str = "http://127.0.0.1:8000/v1"
    llm_api_key: str = "EMPTY"
    llm_model: str = "meta-llama/Llama-4-Scout-17B-16E-Instruct"

    # App
    database_url: str = "sqlite:///./osint_cold_call.db"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
