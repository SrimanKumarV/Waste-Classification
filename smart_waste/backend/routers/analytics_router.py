from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.analytics_service import AnalyticsService

analytics_router = APIRouter(prefix="/api/analytics", tags=["Segregation Analytics"])

@analytics_router.get("/overview")
def get_overview_kpis(days: int = Query(30, ge=1, le=180), db: Session = Depends(get_db)):
    """Returns top-level KPIs: segregation efficiency, contamination rate, total audits, etc."""
    return AnalyticsService.get_overview_kpis(db, days=days)

@analytics_router.get("/locations")
def get_location_rankings(days: int = Query(30, ge=1, le=180), db: Session = Depends(get_db)):
    """Returns location segregation performance for campus heatmaps."""
    return AnalyticsService.get_location_efficiency(db, days=days)

@analytics_router.get("/waste")
def get_waste_distribution(days: int = Query(30, ge=1, le=180), db: Session = Depends(get_db)):
    """Returns waste category and 12-class distribution along with top contaminants."""
    return AnalyticsService.get_waste_distribution(db, days=days)

@analytics_router.get("/trends")
def get_temporal_trends(days: int = Query(14, ge=3, le=60), db: Session = Depends(get_db)):
    """Returns daily trend lines of audits, efficiency %, and contamination."""
    return AnalyticsService.get_temporal_trends(db, days=days)
