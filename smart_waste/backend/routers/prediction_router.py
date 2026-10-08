from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.schemas import Bin
from ..services.prediction_service import prediction_service

prediction_router = APIRouter(prefix="/api/predictions", tags=["Predictive Analytics"])

@prediction_router.get("/bins/{bin_id}")
def predict_bin(bin_id: str, db: Session = Depends(get_db)):
    """Predicts future fill level (4h, 8h, 24h) and expected time to critical capacity."""
    res = prediction_service.predict_bin_fill(db, bin_id)
    if not res:
        raise HTTPException(status_code=404, detail="Bin not found")
    return res

@prediction_router.get("/all")
def predict_all_bins(db: Session = Depends(get_db)):
    """Returns predictive forecasts for all active bins."""
    bins = db.query(Bin).all()
    results = []
    for b in bins:
        pred = prediction_service.predict_bin_fill(db, b.id)
        if pred:
            results.append(pred)
    return results

@prediction_router.get("/trend")
def predict_segregation_trend(db: Session = Depends(get_db)):
    """Predicts next week's segregation efficiency trend from moving averages."""
    return prediction_service.predict_segregation_trend(db)
