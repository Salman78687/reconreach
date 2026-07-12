from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from models.lead import Lead, EnrichmentStatus
from osint.pipeline import enrich_lead

router = APIRouter(prefix="/enrichment", tags=["enrichment"])


async def _run_enrichment(lead_id: int):
    """Background task — runs the OSINT pipeline and saves results to DB."""
    from core.database import SessionLocal
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return

        lead.enrichment_status = EnrichmentStatus.IN_PROGRESS
        db.commit()

        profile = await enrich_lead(lead.input_value, lead.input_type)

        import json
        lead.name = profile.name
        lead.job_title = profile.job_title
        lead.linkedin_url = profile.linkedin_url
        lead.twitter_url = profile.twitter_url
        lead.github_url = profile.github_url
        lead.bio = profile.bio
        lead.recent_posts = json.dumps(profile.recent_posts)
        lead.interests = json.dumps(profile.interests)
        lead.company_name = profile.company_name
        lead.company_industry = profile.company_industry
        lead.company_size = profile.company_size
        lead.company_website = profile.company_website
        lead.company_description = profile.company_description
        lead.recent_news = json.dumps(profile.recent_news)
        lead.enrichment_sources = json.dumps(profile.enrichment_sources)
        lead.raw_analysis = json.dumps(profile.raw_analysis)
        lead.enrichment_score = profile.compute_score()
        lead.enrichment_status = EnrichmentStatus.DONE

    except Exception as e:
        lead.enrichment_status = EnrichmentStatus.FAILED
        lead.error_message = str(e)

    finally:
        db.commit()
        db.close()


@router.post("/{lead_id}")
async def trigger_enrichment(
    lead_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Kick off OSINT enrichment for a single lead (async background task)."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    if lead.enrichment_status == EnrichmentStatus.IN_PROGRESS:
        return {"message": "Enrichment already in progress."}

    lead.enrichment_status = EnrichmentStatus.PENDING
    db.commit()

    background_tasks.add_task(_run_enrichment, lead_id)
    return {"message": "Enrichment started.", "lead_id": lead_id}


@router.post("/batch/all")
async def enrich_all_leads(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Enrich all pending/failed leads."""
    leads = db.query(Lead).filter(
        Lead.enrichment_status.in_([EnrichmentStatus.PENDING, EnrichmentStatus.FAILED])
    ).all()

    for lead in leads:
        lead.enrichment_status = EnrichmentStatus.PENDING
        background_tasks.add_task(_run_enrichment, lead.id)

    db.commit()
    return {"message": f"Enrichment queued for {len(leads)} leads."}
