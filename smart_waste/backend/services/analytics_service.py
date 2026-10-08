from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case

from ..models.schemas import WasteAudit, Location, Bin, SensorReading

class AnalyticsService:
    @staticmethod
    def get_overview_kpis(db: Session, days: int = 30) -> Dict[str, Any]:
        """Calculates core KPI metrics directly from database records."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        total_audits = db.query(WasteAudit).filter(WasteAudit.created_at >= cutoff).count()
        correct_count = db.query(WasteAudit).filter(
            WasteAudit.created_at >= cutoff,
            WasteAudit.segregation_status == "CORRECT"
        ).count()
        incorrect_count = db.query(WasteAudit).filter(
            WasteAudit.created_at >= cutoff,
            WasteAudit.segregation_status == "INCORRECT"
        ).count()
        uncertain_count = db.query(WasteAudit).filter(
            WasteAudit.created_at >= cutoff,
            WasteAudit.segregation_status == "UNCERTAIN"
        ).count()

        efficiency = round((correct_count / total_audits * 100), 1) if total_audits > 0 else 0.0
        contamination_rate = round((incorrect_count / total_audits * 100), 1) if total_audits > 0 else 0.0

        # Average confidence & latency
        avg_conf_res = db.query(func.avg(WasteAudit.confidence)).filter(WasteAudit.created_at >= cutoff).scalar()
        avg_confidence = round(float(avg_conf_res or 0.0) * 100, 1)

        avg_lat_res = db.query(func.avg(WasteAudit.response_time_ms)).filter(WasteAudit.created_at >= cutoff).scalar()
        avg_response_time = round(float(avg_lat_res or 0.0), 1)

        # Bins & IoT status
        total_bins = db.query(Bin).count()
        critical_bins = db.query(Bin).filter(Bin.status == "CRITICAL").count()
        high_bins = db.query(Bin).filter(Bin.status == "HIGH").count()

        # Today's audits
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_audits = db.query(WasteAudit).filter(WasteAudit.created_at >= today_start).count()

        return {
            "total_audits": total_audits,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "uncertain_count": uncertain_count,
            "segregation_efficiency_pct": efficiency,
            "contamination_rate_pct": contamination_rate,
            "avg_confidence_pct": avg_confidence,
            "avg_response_time_ms": avg_response_time,
            "total_bins": total_bins,
            "critical_bins": critical_bins,
            "high_bins": high_bins,
            "today_audits": today_audits,
            "reporting_period_days": days
        }

    @staticmethod
    def get_location_efficiency(db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """Calculates segregation efficiency and contamination per campus location for heatmaps."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        locations = db.query(Location).all()
        results = []

        for loc in locations:
            total = db.query(WasteAudit).filter(
                WasteAudit.location_id == loc.id,
                WasteAudit.created_at >= cutoff
            ).count()
            
            correct = db.query(WasteAudit).filter(
                WasteAudit.location_id == loc.id,
                WasteAudit.created_at >= cutoff,
                WasteAudit.segregation_status == "CORRECT"
            ).count()

            incorrect = db.query(WasteAudit).filter(
                WasteAudit.location_id == loc.id,
                WasteAudit.created_at >= cutoff,
                WasteAudit.segregation_status == "INCORRECT"
            ).count()

            efficiency = round((correct / total * 100), 1) if total > 0 else 0.0
            contamination = round((incorrect / total * 100), 1) if total > 0 else 0.0

            # Status color grading
            if efficiency >= 85:
                performance = "EXCELLENT"
                color = "#10b981"  # Emerald
            elif efficiency >= 70:
                performance = "GOOD"
                color = "#3b82f6"  # Blue
            elif efficiency >= 55:
                performance = "MODERATE"
                color = "#f59e0b"  # Amber
            else:
                performance = "CRITICAL"
                color = "#ef4444"  # Red

            results.append({
                "location_id": loc.id,
                "location_name": loc.name,
                "total_audits": total,
                "correct_audits": correct,
                "incorrect_audits": incorrect,
                "efficiency_pct": efficiency,
                "contamination_pct": contamination,
                "performance_tier": performance,
                "heatmap_color": color
            })

        # Sort by efficiency ascending to highlight problem locations first
        return sorted(results, key=lambda x: x["efficiency_pct"])

    @staticmethod
    def get_waste_distribution(db: Session, days: int = 30) -> Dict[str, Any]:
        """Calculates category and class distributions from audits."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Categories
        cat_counts = (
            db.query(WasteAudit.waste_category, func.count(WasteAudit.id))
            .filter(WasteAudit.created_at >= cutoff)
            .group_by(WasteAudit.waste_category)
            .all()
        )
        categories = {cat: count for cat, count in cat_counts}

        # Detailed classes (top 12)
        class_counts = (
            db.query(WasteAudit.waste_class, func.count(WasteAudit.id))
            .filter(WasteAudit.created_at >= cutoff)
            .group_by(WasteAudit.waste_class)
            .order_by(desc(func.count(WasteAudit.id)))
            .all()
        )
        classes = {cls: count for cls, count in class_counts}

        # Contamination by waste type (which items are most misplaced)
        contam_counts = (
            db.query(WasteAudit.waste_class, func.count(WasteAudit.id))
            .filter(WasteAudit.created_at >= cutoff, WasteAudit.segregation_status == "INCORRECT")
            .group_by(WasteAudit.waste_class)
            .order_by(desc(func.count(WasteAudit.id)))
            .limit(5)
            .all()
        )
        top_contaminants = [{ "item": cls, "count": count } for cls, count in contam_counts]

        return {
            "categories": categories,
            "classes": classes,
            "top_contaminants": top_contaminants
        }

    @staticmethod
    def get_temporal_trends(db: Session, days: int = 14) -> List[Dict[str, Any]]:
        """Returns daily audit volume and efficiency for line/bar charts."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        trends = []

        for i in range(days):
            day_start = (cutoff + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            total = db.query(WasteAudit).filter(
                WasteAudit.created_at >= day_start,
                WasteAudit.created_at < day_end
            ).count()

            correct = db.query(WasteAudit).filter(
                WasteAudit.created_at >= day_start,
                WasteAudit.created_at < day_end,
                WasteAudit.segregation_status == "CORRECT"
            ).count()

            eff = round((correct / total * 100), 1) if total > 0 else 0.0

            trends.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "display_date": day_start.strftime("%b %d"),
                "total": total,
                "correct": correct,
                "incorrect": total - correct,
                "efficiency_pct": eff
            })

        return trends
