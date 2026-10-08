import io
import csv
from datetime import datetime
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schemas import WasteAudit, Bin, Location
from ..services.analytics_service import AnalyticsService
from ..services.energy_service import EnergyAnalyticsService

report_router = APIRouter(prefix="/api/reports", tags=["Reports & Export"])

@report_router.get("/summary")
def get_report_summary(db: Session = Depends(get_db)):
    """Consolidates complete system auditing, IoT, and energy metrics into an academic report."""
    kpis = AnalyticsService.get_overview_kpis(db, days=30)
    locations = AnalyticsService.get_location_efficiency(db, days=30)
    waste = AnalyticsService.get_waste_distribution(db, days=30)
    energy = EnergyAnalyticsService.get_energy_collection_plan(db)

    return {
        "report_title": "Smart Waste Segregation Analytics — Comprehensive Audit Report",
        "generated_at": datetime.utcnow().isoformat(),
        "academic_domain": "IoT Architecture, Deep Learning, SDG 7 Clean Energy",
        "key_performance_indicators": kpis,
        "location_efficiency_ranking": locations,
        "waste_distribution": waste,
        "energy_optimization_sdg7": energy
    }

@report_router.get("/export-csv")
def export_audits_csv(db: Session = Depends(get_db)):
    """Exports waste audit events as downloadable CSV format."""
    audits = db.query(WasteAudit).order_by(WasteAudit.created_at.desc()).limit(1000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Audit ID", "Timestamp (UTC)", "Location", "Assigned Bin",
        "Waste Class", "Category", "Confidence (%)", "Expected Bin",
        "Actual Bin", "Segregation Status", "Model Used", "Response Time (ms)"
    ])

    for a in audits:
        loc_name = a.location.name if a.location else "Unknown"
        writer.writerow([
            a.id,
            a.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            loc_name,
            a.bin_id or "N/A",
            a.waste_class,
            a.waste_category,
            f"{a.confidence * 100:.1f}",
            a.expected_bin,
            a.actual_bin,
            a.segregation_status,
            a.model_name,
            f"{a.response_time_ms:.1f}"
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=waste_audits_report.csv"}
    )
