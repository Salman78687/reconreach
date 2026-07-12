import io
import json
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from models.lead import Lead, LeadType, EnrichmentStatus

router = APIRouter(prefix="/leads", tags=["leads"])


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class LeadOut(BaseModel):
    id: int
    input_value: str
    input_type: str
    enrichment_status: str
    enrichment_score: int
    name: Optional[str]
    job_title: Optional[str]
    linkedin_url: Optional[str]
    twitter_url: Optional[str]
    github_url: Optional[str]
    bio: Optional[str]
    recent_posts: list[str]
    interests: list[str]
    company_name: Optional[str]
    company_industry: Optional[str]
    company_size: Optional[str]
    company_website: Optional[str]
    company_description: Optional[str]
    recent_news: list[str]
    enrichment_sources: list[str]
    raw_analysis: dict
    error_message: Optional[str]
    generated_email: Optional[str]
    generated_call_script: Optional[str]
    generated_linkedin_msg: Optional[str]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_lead(cls, lead: Lead) -> "LeadOut":
        return cls(
            id=lead.id,
            input_value=lead.input_value,
            input_type=lead.input_type,
            enrichment_status=lead.enrichment_status,
            enrichment_score=lead.enrichment_score,
            name=lead.name,
            job_title=lead.job_title,
            linkedin_url=lead.linkedin_url,
            twitter_url=lead.twitter_url,
            github_url=lead.github_url,
            bio=lead.bio,
            recent_posts=lead.get_recent_posts(),
            interests=lead.get_interests(),
            company_name=lead.company_name,
            company_industry=lead.company_industry,
            company_size=lead.company_size,
            company_website=lead.company_website,
            company_description=lead.company_description,
            recent_news=lead.get_recent_news(),
            enrichment_sources=lead.get_enrichment_sources(),
            raw_analysis=lead.get_raw_analysis(),
            error_message=lead.error_message,
            generated_email=lead.generated_email,
            generated_call_script=lead.generated_call_script,
            generated_linkedin_msg=lead.generated_linkedin_msg,
        )


def _detect_lead_type(value: str) -> LeadType:
    """Heuristic: if it contains '@' it's an email, otherwise phone."""
    return LeadType.EMAIL if "@" in value else LeadType.PHONE


# ── Endpoints ────────────────────────────────────────────────────────────────

class SingleLeadIn(BaseModel):
    value: str


@router.post("/single", response_model=LeadOut)
def add_single_lead(body: SingleLeadIn, db: Session = Depends(get_db)):
    """Add one lead by email or phone number."""
    value = body.value.strip()
    if not value:
        raise HTTPException(status_code=400, detail="Value cannot be empty.")

    existing = db.query(Lead).filter(Lead.input_value == value).first()
    if existing:
        raise HTTPException(status_code=409, detail="Lead already exists.")

    lead = Lead(
        input_value=value,
        input_type=_detect_lead_type(value),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return LeadOut.from_orm_lead(lead)


@router.post("/upload", response_model=list[LeadOut])
async def upload_leads(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Accept a CSV with a column named 'email', 'phone', or 'lead'."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse CSV file.")

    # Find the lead column
    col = None
    for candidate in ["email", "phone", "lead", "value"]:
        if candidate in [c.lower() for c in df.columns]:
            col = next(c for c in df.columns if c.lower() == candidate)
            break

    if col is None:
        raise HTTPException(
            status_code=400,
            detail="CSV must have a column named 'email', 'phone', or 'lead'.",
        )

    created: list[Lead] = []
    for raw_value in df[col].dropna().unique():
        value = str(raw_value).strip()
        if not value:
            continue

        # Skip duplicates already in DB
        existing = db.query(Lead).filter(Lead.input_value == value).first()
        if existing:
            continue

        lead = Lead(
            input_value=value,
            input_type=_detect_lead_type(value),
            enrichment_status=EnrichmentStatus.PENDING,
        )
        db.add(lead)
        created.append(lead)

    db.commit()
    for lead in created:
        db.refresh(lead)

    return [LeadOut.from_orm_lead(l) for l in created]


@router.get("", response_model=list[LeadOut])
def list_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return [LeadOut.from_orm_lead(l) for l in leads]


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return LeadOut.from_orm_lead(lead)


@router.delete("/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    db.delete(lead)
    db.commit()
    return {"ok": True}


@router.delete("")
def delete_all_leads(db: Session = Depends(get_db)):
    db.query(Lead).delete()
    db.commit()
    return {"ok": True}
