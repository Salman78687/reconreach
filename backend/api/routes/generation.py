from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from models.lead import Lead, EnrichmentStatus
from llm.client import LLMClient

router = APIRouter(prefix="/generation", tags=["generation"])


class GenerationRequest(BaseModel):
    product_name: str
    product_description: str
    key_value_props: list[str]
    target_pain_point: str
    output_types: list[str]  # ["email", "call_script", "linkedin_msg"]


class GenerationResponse(BaseModel):
    lead_id: int
    email: str | None = None
    call_script: str | None = None
    linkedin_msg: str | None = None


@router.post("/{lead_id}", response_model=GenerationResponse)
async def generate_outreach(
    lead_id: int,
    req: GenerationRequest,
    db: Session = Depends(get_db),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    if lead.enrichment_status != EnrichmentStatus.DONE:
        raise HTTPException(
            status_code=400,
            detail="Lead must be fully enriched before generating outreach.",
        )

    client = LLMClient()

    seller_ctx = {
        "product_name": req.product_name,
        "product_description": req.product_description,
        "key_value_props": req.key_value_props,
        "target_pain_point": req.target_pain_point,
    }

    recipient_ctx = {
        "name": lead.name,
        "job_title": lead.job_title,
        "company_name": lead.company_name,
        "company_industry": lead.company_industry,
        "bio": lead.bio,
        "recent_posts": lead.get_recent_posts(),
        "interests": lead.get_interests(),
        "recent_news": lead.get_recent_news(),
        "linkedin_url": lead.linkedin_url,
    }

    result = GenerationResponse(lead_id=lead_id)

    if "email" in req.output_types:
        from llm.generators.email import generate_cold_email
        result.email = await generate_cold_email(client, seller_ctx, recipient_ctx)
        lead.generated_email = result.email

    if "call_script" in req.output_types:
        from llm.generators.call_script import generate_call_script
        result.call_script = await generate_call_script(client, seller_ctx, recipient_ctx)
        lead.generated_call_script = result.call_script

    if "linkedin_msg" in req.output_types:
        from llm.generators.linkedin_msg import generate_linkedin_msg
        result.linkedin_msg = await generate_linkedin_msg(client, seller_ctx, recipient_ctx)
        lead.generated_linkedin_msg = result.linkedin_msg

    db.commit()
    return result
