from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models.schemas import Bin, SensorReading, Location
from ..schemas.api_schemas import (
    SensorReadingCreate, SensorReadingResponse, BinResponse
)
from ..services.iot_service import IoTService

iot_router = APIRouter(prefix="/api", tags=["IoT & Bins"])

class SimulateManualRequest(BaseModel):
    bin_id: str
    fill_percentage: float
    weight_kg: float
    temperature: Optional[float] = 27.0
    gas_level: Optional[float] = 60.0

@iot_router.get("/iot/bins")
def get_all_bins(db: Session = Depends(get_db)):
    """Returns all monitored bins with their real-time sensor metrics and status."""
    return IoTService.get_all_bins(db)

@iot_router.get("/iot/bins/{bin_id}")
def get_bin_detail(bin_id: str, db: Session = Depends(get_db)):
    """Returns single bin details and recent sensor history."""
    b = db.query(Bin).filter(Bin.id == bin_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bin not found")

    recent_readings = (
        db.query(SensorReading)
        .filter(SensorReading.bin_id == bin_id)
        .order_by(SensorReading.timestamp.desc())
        .limit(20)
        .all()
    )

    return {
        "bin": {
            "id": b.id,
            "location_name": b.location.name if b.location else "Unknown",
            "bin_type": b.bin_type,
            "capacity_kg": b.capacity_kg,
            "status": b.status,
            "fill_percentage": b.fill_percentage,
            "weight_kg": b.weight_kg,
            "temperature": b.temperature,
            "gas_level": b.gas_level,
            "last_updated": b.last_updated.isoformat() if b.last_updated else None
        },
        "history": [
            {
                "fill_percentage": r.fill_percentage,
                "weight_kg": r.weight_kg,
                "temperature": r.temperature,
                "gas_level": r.gas_level,
                "timestamp": r.timestamp.isoformat()
            }
            for r in recent_readings
        ]
    }

@iot_router.post("/iot/sensor", response_model=SensorReadingResponse)
def ingest_sensor_reading(reading_in: SensorReadingCreate, db: Session = Depends(get_db)):
    """
    ESP32 / IoT Hardware Ingestion Endpoint.
    Receives JSON telemetry from gateways and updates live bin status.
    """
    reading = IoTService.record_reading(db, reading_in)
    return reading

@iot_router.post("/iot/simulate")
def simulate_tick(req: Optional[SimulateManualRequest] = None, db: Session = Depends(get_db)):
    """
    IoT Simulation Mode Endpoint:
    Either executes one realistic time-step simulation tick across all bins,
    or accepts an operator's manual slider override for demonstration.
    """
    if req and req.bin_id:
        reading_in = SensorReadingCreate(
            bin_id=req.bin_id,
            fill_percentage=req.fill_percentage,
            weight_kg=req.weight_kg,
            temperature=req.temperature or 27.0,
            gas_level=req.gas_level or 60.0,
            device_id="SIMULATOR-MANUAL"
        )
        IoTService.record_reading(db, reading_in)
        return {
            "success": True,
            "mode": "MANUAL_OVERRIDE",
            "message": f"Updated {req.bin_id} with custom telemetry reading."
        }
    else:
        updates = IoTService.simulate_telemetry_tick(db)
        return {
            "success": True,
            "mode": "DIURNAL_TICK",
            "updated_bins_count": len(updates),
            "readings": updates
        }

@iot_router.get("/locations")
def get_locations(db: Session = Depends(get_db)):
    """Returns list of campus locations."""
    locs = db.query(Location).all()
    return [
        {
            "id": l.id,
            "name": l.name,
            "description": l.description,
            "latitude": l.latitude,
            "longitude": l.longitude
        }
        for l in locs
    ]
