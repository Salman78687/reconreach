"""Main OSINT pipeline orchestrator."""
from models.enrichment import EnrichedProfile
from models.lead import LeadType


async def enrich_lead(input_value: str, input_type: str) -> EnrichedProfile:
    if input_type == LeadType.EMAIL:
        from osint.email_enricher import enrich_email
        return await enrich_email(input_value)
    elif input_type == LeadType.PHONE:
        from osint.phone_enricher import enrich_phone
        return await enrich_phone(input_value)
    else:
        raise ValueError(f"Unknown lead type: {input_type}")
