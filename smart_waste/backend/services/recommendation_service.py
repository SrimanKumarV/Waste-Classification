from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from ..models.schemas import Recommendation, Location, Bin, WasteAudit
from ..config import CRITICAL_FILL_THRESHOLD

class RecommendationService:
    @staticmethod
    def generate_recommendations(db: Session) -> List[Recommendation]:
        """
        Decision-support engine: Analyzes audits, bin fill levels, and contamination rates
        to generate prioritized, actionable recommendations with transparent justifications.
        """
        now = datetime.utcnow()
        cutoff_7d = now - timedelta(days=7)
        new_recs = []

        # 1. Critical Bin Fill & Imminent Overflow Check
        bins = db.query(Bin).all()
        for b in bins:
            loc_name = b.location.name if b.location else "Unknown"
            if b.fill_percentage >= CRITICAL_FILL_THRESHOLD:
                # Check if an active recommendation already exists
                existing = db.query(Recommendation).filter(
                    Recommendation.title.like(f"%{b.id}%"),
                    Recommendation.status == "ACTIVE"
                ).first()
                if not existing:
                    rec = Recommendation(
                        location_id=b.location_id,
                        priority="CRITICAL",
                        title=f"Immediate Collection Required: {b.id}",
                        reason=(
                            f"{b.id} ({b.bin_type}) in {loc_name} has reached {b.fill_percentage}% capacity "
                            f"(Weight: {b.weight_kg}kg, Gas Index: {b.gas_level} ppm). Exceeds 90% safety limit."
                        ),
                        recommendation=f"Dispatch collection crew to empty {b.id} immediately before overflow occurs.",
                        expected_benefit="Prevents litter spillage, pest infestation, and public health hazard.",
                        status="ACTIVE",
                        created_at=now
                    )
                    db.add(rec)
                    new_recs.append(rec)

        # 2. Location-wise Segregation Efficiency Analysis
        locations = db.query(Location).all()
        for loc in locations:
            audits = db.query(WasteAudit).filter(
                WasteAudit.location_id == loc.id,
                WasteAudit.created_at >= cutoff_7d
            ).all()

            if len(audits) >= 15:
                correct = sum(1 for a in audits if a.segregation_status == "CORRECT")
                incorrect = sum(1 for a in audits if a.segregation_status == "INCORRECT")
                eff = (correct / len(audits)) * 100
                contam = (incorrect / len(audits)) * 100

                # Check low segregation efficiency
                if eff < 65.0:
                    existing = db.query(Recommendation).filter(
                        Recommendation.location_id == loc.id,
                        Recommendation.title.like("%Awareness Training%"),
                        Recommendation.status == "ACTIVE"
                    ).first()
                    if not existing:
                        rec = Recommendation(
                            location_id=loc.id,
                            priority="HIGH",
                            title=f"Conduct Source Segregation Awareness at {loc.name}",
                            reason=(
                                f"Segregation efficiency in {loc.name} averaged only {eff:.1f}% over the last 7 days "
                                f"({incorrect} incorrect disposals out of {len(audits)} audited items)."
                            ),
                            recommendation=(
                                f"Deploy clear bilingual bin signage, install pictorial sorting guides at disposal points, "
                                f"and schedule a student/staff waste awareness briefing in {loc.name}."
                            ),
                            expected_benefit=f"Expected to improve segregation efficiency by 18-25% within 14 days.",
                            status="ACTIVE",
                            created_at=now
                        )
                        db.add(rec)
                        new_recs.append(rec)

                # Check high plastic / recyclable contamination
                plastic_in_organic = sum(
                    1 for a in audits 
                    if a.waste_class == "plastic" and "Green" in a.actual_bin
                )
                if plastic_in_organic >= 5:
                    existing = db.query(Recommendation).filter(
                        Recommendation.location_id == loc.id,
                        Recommendation.title.like("%Plastic Contamination%"),
                        Recommendation.status == "ACTIVE"
                    ).first()
                    if not existing:
                        rec = Recommendation(
                            location_id=loc.id,
                            priority="HIGH",
                            title=f"Address Plastic Contamination in Organic Bins at {loc.name}",
                            reason=(
                                f"Detected {plastic_in_organic} instances of plastic waste deposited into Organic (Green) bins "
                                f"at {loc.name} in the past week."
                            ),
                            recommendation=(
                                f"Place paired Blue Recyclable bins directly beside Green bins to eliminate lazy dumping, "
                                f"and inspect canteen takeaway packaging policies."
                            ),
                            expected_benefit="Reduces organic compost contamination and safeguards recycling batch purity.",
                            status="ACTIVE",
                            created_at=now
                        )
                        db.add(rec)
                        new_recs.append(rec)

                # Check hazardous battery contamination
                hazardous_misplaced = sum(
                    1 for a in audits
                    if a.waste_category == "Hazardous" and a.segregation_status == "INCORRECT"
                )
                if hazardous_misplaced >= 1:
                    existing = db.query(Recommendation).filter(
                        Recommendation.location_id == loc.id,
                        Recommendation.title.like("%Hazardous%"),
                        Recommendation.status == "ACTIVE"
                    ).first()
                    if not existing:
                        rec = Recommendation(
                            location_id=loc.id,
                            priority="CRITICAL",
                            title=f"Critical: Misplaced Hazardous Waste at {loc.name}",
                            reason=(
                                f"Detected battery/toxic waste disposed into non-hazardous bins in {loc.name}. "
                                f"Poses fire risk and toxic chemical leaching."
                            ),
                            recommendation="Inspect disposal area, verify Red Bin availability, and secure designated e-waste drop point.",
                            expected_benefit="Prevents facility fires and hazardous chemical environmental contamination.",
                            status="ACTIVE",
                            created_at=now
                        )
                        db.add(rec)
                        new_recs.append(rec)

        db.commit()
        return db.query(Recommendation).order_by(
            Recommendation.status.asc(),
            Recommendation.created_at.desc()
        ).all()

    @staticmethod
    def update_recommendation_status(db: Session, rec_id: int, new_status: str) -> bool:
        rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
        if rec:
            rec.status = new_status.upper()
            db.commit()
            return True
        return False
