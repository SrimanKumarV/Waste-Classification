from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schemas import Recommendation
from ..schemas.api_schemas import RecommendationResponse
from ..services.recommendation_service import RecommendationService

recommendation_router = APIRouter(prefix="/api/recommendations", tags=["Decision Support & Recommendations"])

class StatusUpdateRequest(BaseModel):
    status: str  # ACTIVE, ACKNOWLEDGED, RESOLVED

@recommendation_router.get("", response_model=List[RecommendationResponse])
def get_recommendations(db: Session = Depends(get_db)):
    """Returns all decision-support recommendations ordered by priority and recency."""
    recs = db.query(Recommendation).order_by(
        Recommendation.status.asc(),
        Recommendation.created_at.desc()
    ).all()

    results = []
    for r in recs:
        results.append(RecommendationResponse(
            id=r.id,
            location_id=r.location_id,
            location_name=r.location.name if r.location else "All Campus Locations",
            priority=r.priority,
            title=r.title,
            reason=r.reason,
            recommendation=r.recommendation,
            expected_benefit=r.expected_benefit,
            status=r.status,
            created_at=r.created_at
        ))
    return results

@recommendation_router.post("/generate", response_model=List[RecommendationResponse])
def trigger_generation(db: Session = Depends(get_db)):
    """Triggers real-time evaluation of sensor telemetry and segregation audits to generate recommendations."""
    recs = RecommendationService.generate_recommendations(db)
    results = []
    for r in recs:
        results.append(RecommendationResponse(
            id=r.id,
            location_id=r.location_id,
            location_name=r.location.name if r.location else "All Campus Locations",
            priority=r.priority,
            title=r.title,
            reason=r.reason,
            recommendation=r.recommendation,
            expected_benefit=r.expected_benefit,
            status=r.status,
            created_at=r.created_at
        ))
    return results

@recommendation_router.patch("/{rec_id}/status")
def update_status(rec_id: int, req: StatusUpdateRequest, db: Session = Depends(get_db)):
    """Updates recommendation lifecycle status (e.g., ACKNOWLEDGED or RESOLVED)."""
    success = RecommendationService.update_recommendation_status(db, rec_id, req.status)
    if not success:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"success": True, "id": rec_id, "new_status": req.status.upper()}
