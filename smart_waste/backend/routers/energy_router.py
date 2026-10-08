from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.api_schemas import EnergyAnalyticsResponse
from ..services.energy_service import EnergyAnalyticsService

energy_router = APIRouter(prefix="/api/energy", tags=["SDG 7 — Energy-Aware Logistics"])

@energy_router.get("/collection-plan", response_model=EnergyAnalyticsResponse)
def get_energy_plan(db: Session = Depends(get_db)):
    """
    SDG 7 — Affordable and Clean Energy Decision Support Endpoint.
    Compares scheduled fixed collection against on-demand fill-driven routing,
    calculating vehicle trips avoided, fuel savings, and CO2 emissions reduction.
    """
    return EnergyAnalyticsService.get_energy_collection_plan(db)
