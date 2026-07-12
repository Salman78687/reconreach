from dataclasses import dataclass, field


@dataclass
class EnrichedProfile:
    """Intermediate data structure produced by the OSINT pipeline."""

    # Input
    input_value: str
    input_type: str  # "email" | "phone"

    # Person
    name: str | None = None
    job_title: str | None = None
    linkedin_url: str | None = None
    twitter_url: str | None = None
    github_url: str | None = None
    bio: str | None = None
    recent_posts: list[str] = field(default_factory=list)
    interests: list[str] = field(default_factory=list)

    # Company
    company_name: str | None = None
    company_industry: str | None = None
    company_size: str | None = None
    company_website: str | None = None
    company_description: str | None = None
    recent_news: list[str] = field(default_factory=list)

    # Meta
    enrichment_sources: list[str] = field(default_factory=list)
    # Raw per-source data: {"hunter.io/domain": {"status": "success"|"empty"|"error", "data": {...}}}
    raw_analysis: dict = field(default_factory=dict)

    def compute_score(self) -> int:
        """Score 0–100 based on how many fields are populated."""
        scored_fields = [
            self.name, self.job_title, self.linkedin_url, self.twitter_url,
            self.github_url, self.bio, self.company_name, self.company_industry,
            self.company_size, self.company_website, self.company_description,
        ]
        list_fields = [self.recent_posts, self.interests, self.recent_news]

        filled = sum(1 for f in scored_fields if f)
        filled += sum(1 for f in list_fields if f)

        total = len(scored_fields) + len(list_fields)
        return round((filled / total) * 100)
