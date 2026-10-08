from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.schemas import WasteAudit, UserFeedback, Location
from ..schemas.api_schemas import (
    AuditCreate, AuditResponse, FeedbackCreate, FeedbackResponse
)
from ..services.audit_service import AuditService

audit_router = APIRouter(prefix="/api", tags=["Waste Audits & Feedback"])

@audit_router.post("/audits", response_model=AuditResponse)
def record_audit(audit_in: AuditCreate, db: Session = Depends(get_db)):
    """
    Records a completed waste audit event.
    Evaluates expected bin vs user's actual bin and automatically
    computes segregation status (CORRECT, INCORRECT, UNCERTAIN).
    """
    audit = AuditService.create_audit(db, audit_in)
    loc_name = audit.location.name if audit.location else "Unknown"

    resp = AuditResponse(
        id=audit.id,
        user_id=audit.user_id,
        location_id=audit.location_id,
        location_name=loc_name,
        bin_id=audit.bin_id,
        image_url=audit.image_url,
        waste_class=audit.waste_class,
        waste_category=audit.waste_category,
        confidence=audit.confidence,
        expected_bin=audit.expected_bin,
        actual_bin=audit.actual_bin,
        segregation_status=audit.segregation_status,
        model_name=audit.model_name,
        model_version=audit.model_version,
        response_time_ms=audit.response_time_ms,
        created_at=audit.created_at
    )
    return resp

@audit_router.get("/audits")
def get_audits(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    location_id: Optional[int] = None,
    segregation_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieves paginated audit history with optional location or status filtering."""
    audits = AuditService.get_audits(
        db, limit=limit, offset=offset,
        location_id=location_id, segregation_status=segregation_status
    )
    total = db.query(WasteAudit).count()

    results = []
    for a in audits:
        results.append({
            "id": a.id,
            "location_name": a.location.name if a.location else "Unknown",
            "bin_id": a.bin_id,
            "waste_class": a.waste_class,
            "waste_category": a.waste_category,
            "confidence": a.confidence,
            "expected_bin": a.expected_bin,
            "actual_bin": a.actual_bin,
            "segregation_status": a.segregation_status,
            "model_name": a.model_name,
            "response_time_ms": a.response_time_ms,
            "created_at": a.created_at.isoformat()
        })

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "audits": results
    }

@audit_router.post("/feedback")
def submit_feedback(fb_in: FeedbackCreate, db: Session = Depends(get_db)):
    """Submits stakeholder usefulness rating (1-5 stars) and qualitative feedback."""
    feedback = UserFeedback(
        audit_id=fb_in.audit_id,
        rating=fb_in.rating,
        feedback_type=fb_in.feedback_type,
        comments=fb_in.comments
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return {
        "success": True,
        "feedback_id": feedback.id,
        "rating": feedback.rating,
        "message": "Thank you for your feedback!"
    }

@audit_router.get("/feedback/stats")
def get_feedback_stats(db: Session = Depends(get_db)):
    """Returns average stakeholder rating and total response count."""
    total = db.query(UserFeedback).count()
    avg_rating = db.query(func.avg(UserFeedback.rating)).scalar() or 0.0
    recent = db.query(UserFeedback).order_by(UserFeedback.created_at.desc()).limit(10).all()

    return {
        "total_responses": total,
        "average_usefulness_rating": round(float(avg_rating), 2),
        "recent_feedback": [
            {
                "id": f.id,
                "rating": f.rating,
                "comments": f.comments,
                "created_at": f.created_at.isoformat()
            }
            for f in recent
        ]
    }
