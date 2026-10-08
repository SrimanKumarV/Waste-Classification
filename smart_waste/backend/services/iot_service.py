import math
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models.schemas import Bin, SensorReading, Location
from ..schemas.api_schemas import SensorReadingCreate
from ..config import (
    CRITICAL_FILL_THRESHOLD, HIGH_FILL_THRESHOLD, MODERATE_FILL_THRESHOLD
)

class IoTService:
    @staticmethod
    def calculate_bin_status(fill_pct: float) -> str:
        """Determines bin status level based on fill percentage."""
        if fill_pct >= CRITICAL_FILL_THRESHOLD:
            return "CRITICAL"
        elif fill_pct >= HIGH_FILL_THRESHOLD:
            return "HIGH"
        elif fill_pct >= MODERATE_FILL_THRESHOLD:
            return "MODERATE"
        return "NORMAL"

    @staticmethod
    def record_reading(db: Session, reading_in: SensorReadingCreate) -> SensorReading:
        """Records sensor telemetry and updates bin current state."""
        status = IoTService.calculate_bin_status(reading_in.fill_percentage)

        # Update bin record
        bin_obj = db.query(Bin).filter(Bin.id == reading_in.bin_id).first()
        if bin_obj:
            bin_obj.fill_percentage = round(reading_in.fill_percentage, 1)
            bin_obj.weight_kg = round(reading_in.weight_kg, 2)
            bin_obj.temperature = round(reading_in.temperature, 1)
            bin_obj.gas_level = round(reading_in.gas_level, 1)
            bin_obj.status = status
            bin_obj.last_updated = datetime.utcnow()

        # Add to telemetry history
        reading = SensorReading(
            bin_id=reading_in.bin_id,
            fill_percentage=round(reading_in.fill_percentage, 1),
            weight_kg=round(reading_in.weight_kg, 2),
            temperature=round(reading_in.temperature, 1),
            gas_level=round(reading_in.gas_level, 1),
            timestamp=datetime.utcnow()
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)
        return reading

    @staticmethod
    def get_all_bins(db: Session) -> List[Dict[str, Any]]:
        """Returns all bins with their live status and location details."""
        bins = db.query(Bin).all()
        result = []
        for b in bins:
            result.append({
                "id": b.id,
                "location_id": b.location_id,
                "location_name": b.location.name if b.location else "Unknown",
                "bin_type": b.bin_type,
                "capacity_kg": b.capacity_kg,
                "status": b.status,
                "fill_percentage": b.fill_percentage,
                "weight_kg": b.weight_kg,
                "temperature": b.temperature,
                "gas_level": b.gas_level,
                "last_updated": b.last_updated.isoformat() if b.last_updated else None
            })
        return result

    @staticmethod
    def simulate_telemetry_tick(db: Session) -> List[Dict[str, Any]]:
        """
        Simulation Mode Engine:
        Generates realistic diurnal waste accumulation patterns across all bins.
        """
        now = datetime.utcnow()
        hour = now.hour

        # Diurnal pattern multiplier
        if 12 <= hour <= 14:       # Lunch peak
            rate_factor = 2.5
        elif 8 <= hour <= 11:      # Morning work
            rate_factor = 1.4
        elif 17 <= hour <= 20:     # Evening rush
            rate_factor = 2.0
        elif 22 <= hour or hour <= 6: # Night hours
            rate_factor = 0.2
        else:
            rate_factor = 1.0

        updated_readings = []
        bins = db.query(Bin).all()

        for b in bins:
            # Different bin types have different fill speeds
            type_multiplier = 1.3 if "Organic" in b.bin_type else (1.0 if "Recyclable" in b.bin_type else 0.4)
            delta = random.uniform(0.8, 2.5) * rate_factor * type_multiplier

            new_fill = b.fill_percentage + delta

            # If bin exceeded 98%, simulate an automatic collection cycle emptying it
            if new_fill >= 98.0:
                new_fill = random.uniform(3.0, 8.0)
                b.weight_kg = round(new_fill * 0.22, 2)
            else:
                new_fill = min(100.0, new_fill)
                # Weight correlates with fill percentage
                density = 0.24 if "Organic" in b.bin_type else 0.18
                b.weight_kg = round(min(b.capacity_kg, new_fill * density + random.uniform(-0.3, 0.3)), 2)

            # Temperature and gas modeling
            b.fill_percentage = round(new_fill, 1)
            b.status = IoTService.calculate_bin_status(new_fill)
            b.temperature = round(26.0 + 4.0 * math.sin(now.hour / 24 * 2 * math.pi) + random.uniform(-0.5, 0.5), 1)
            
            # Organic bins emit higher gas when full
            base_gas = 120.0 if "Organic" in b.bin_type else 45.0
            b.gas_level = round(base_gas + (new_fill * 1.8) + random.uniform(-5.0, 5.0), 1)
            b.last_updated = now

            reading = SensorReading(
                bin_id=b.id,
                fill_percentage=b.fill_percentage,
                weight_kg=b.weight_kg,
                temperature=b.temperature,
                gas_level=b.gas_level,
                timestamp=now
            )
            db.add(reading)
            updated_readings.append({
                "bin_id": b.id,
                "fill_percentage": b.fill_percentage,
                "weight_kg": b.weight_kg,
                "temperature": b.temperature,
                "gas_level": b.gas_level,
                "status": b.status
            })

        db.commit()
        return updated_readings
