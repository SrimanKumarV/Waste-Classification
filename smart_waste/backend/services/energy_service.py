from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..models.schemas import Bin
from ..config import (
    TRADITIONAL_COLLECTION_TRIPS_PER_WEEK,
    AVERAGE_DISTANCE_PER_TRIP_KM,
    AVERAGE_FUEL_CONSUMPTION_L_PER_KM,
    DIESEL_ENERGY_KWH_PER_LITER,
    CO2_KG_PER_LITER_DIESEL,
    HIGH_FILL_THRESHOLD
)

class EnergyAnalyticsService:
    @staticmethod
    def get_energy_collection_plan(db: Session) -> Dict[str, Any]:
        """
        SDG 7 — Affordable and Clean Energy Decision Support Layer.
        Compares static legacy municipal collection against on-demand,
        fill-level-driven smart dispatch to minimize vehicle travel and emissions.
        """
        all_bins = db.query(Bin).all()
        total_bins = len(all_bins)

        # Bins requiring immediate or near-term service (fill >= 75%)
        actionable_bins = [b for b in all_bins if b.fill_percentage >= HIGH_FILL_THRESHOLD]

        # Prioritize sequence by fill percentage descending and hazardous status
        sorted_route = sorted(
            all_bins,
            key=lambda x: (x.fill_percentage >= 90.0, x.fill_percentage),
            reverse=True
        )

        route_sequence = []
        for rank, b in enumerate(sorted_route, 1):
            needs_pickup = b.fill_percentage >= HIGH_FILL_THRESHOLD
            urgency = "IMMEDIATE" if b.fill_percentage >= 90.0 else ("SCHEDULED" if b.fill_percentage >= 75.0 else "DEFER")
            route_sequence.append({
                "sequence_order": rank,
                "bin_id": b.id,
                "location_name": b.location.name if b.location else "Unknown",
                "bin_type": b.bin_type,
                "fill_percentage": b.fill_percentage,
                "weight_kg": b.weight_kg,
                "status": b.status,
                "dispatch_action": urgency,
                "requires_collection": needs_pickup
            })

        # Modeled savings calculation
        fraction_needing_service = len(actionable_bins) / max(1, total_bins)
        
        # In smart model, trips are scaled with actual bin demand
        traditional_trips = TRADITIONAL_COLLECTION_TRIPS_PER_WEEK
        smart_trips = max(4, round(traditional_trips * max(0.35, fraction_needing_service)))
        trips_avoided = max(0, traditional_trips - smart_trips)

        # Distance & Energy metrics
        km_avoided = trips_avoided * AVERAGE_DISTANCE_PER_TRIP_KM
        fuel_saved_l = round(km_avoided * AVERAGE_FUEL_CONSUMPTION_L_PER_KM, 2)
        energy_saved_kwh = round(fuel_saved_l * DIESEL_ENERGY_KWH_PER_LITER, 2)
        co2_reduction_kg = round(fuel_saved_l * CO2_KG_PER_LITER_DIESEL, 2)
        percent_reduction = round((trips_avoided / traditional_trips) * 100, 1)

        return {
            "traditional_trips_week": traditional_trips,
            "optimized_trips_week": smart_trips,
            "trips_avoided_week": trips_avoided,
            "fuel_saved_liters": fuel_saved_l,
            "energy_saved_kwh": energy_saved_kwh,
            "co2_reduction_kg": co2_reduction_kg,
            "percent_reduction": percent_reduction,
            "actionable_bins_count": len(actionable_bins),
            "total_bins_monitored": total_bins,
            "priority_collection_route": route_sequence[:6],  # Top 6 priority stops
            "sdg_alignment": "SDG 7: Affordable and Clean Energy — Energy-Aware Logistics",
            "methodology": "Modeled / Estimated from Campus Logistics Baseline (Not Directly Metered)"
        }
