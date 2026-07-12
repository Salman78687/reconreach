import json
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from core.database import Base


class LeadType(str, PyEnum):
    EMAIL = "email"
    PHONE = "phone"


class EnrichmentStatus(str, PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    input_value = Column(String, nullable=False)
    input_type = Column(Enum(LeadType), nullable=False)
    enrichment_status = Column(Enum(EnrichmentStatus), default=EnrichmentStatus.PENDING)
    enrichment_score = Column(Integer, default=0)

    # Enriched person fields
    name = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    twitter_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    recent_posts = Column(Text, default="[]")   # JSON list of strings
    interests = Column(Text, default="[]")       # JSON list of strings

    # Enriched company fields
    company_name = Column(String, nullable=True)
    company_industry = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    company_website = Column(String, nullable=True)
    company_description = Column(Text, nullable=True)
    recent_news = Column(Text, default="[]")     # JSON list of strings

    # Meta
    enrichment_sources = Column(Text, default="[]")  # JSON list of strings
    raw_analysis = Column(Text, default="{}")         # JSON dict: source → {status, data}
    error_message = Column(Text, nullable=True)

    # Generated outputs (stored as JSON)
    generated_email = Column(Text, nullable=True)
    generated_call_script = Column(Text, nullable=True)
    generated_linkedin_msg = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    def get_recent_posts(self) -> list[str]:
        return json.loads(self.recent_posts or "[]")

    def get_interests(self) -> list[str]:
        return json.loads(self.interests or "[]")

    def get_recent_news(self) -> list[str]:
        return json.loads(self.recent_news or "[]")

    def get_enrichment_sources(self) -> list[str]:
        return json.loads(self.enrichment_sources or "[]")

    def get_raw_analysis(self) -> dict:
        return json.loads(self.raw_analysis or "{}")
