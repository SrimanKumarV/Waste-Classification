from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models.schemas import WasteAudit, Location, Bin
from ..schemas.api_schemas import AuditCreate
from ..config import CLASS_BIN_MAP, CLASS_CATEGORY_MAP, MODEL_CONFIDENCE_THRESHOLD

class AuditService:
    @staticmethod
    def create_audit(db: Session, audit_in: AuditCreate) -> WasteAudit:
        """
        Core academic function: Evaluates expected bin vs actual bin,
        computes segregation status (CORRECT, INCORRECT, UNCERTAIN),
        and records the audit event in the database.
        """
        waste_class = audit_in.waste_class.lower().strip()
        expected_bin = CLASS_BIN_MAP.get(waste_class, "Recyclable (Blue Bin)")
        waste_category = CLASS_CATEGORY_MAP.get(waste_class, "Recyclable")

        # Determine segregation status
        if audit_in.confidence < MODEL_CONFIDENCE_THRESHOLD:
            segregation_status = "UNCERTAIN"
        elif audit_in.actual_bin.strip().lower() == expected_bin.strip().lower():
            segregation_status = "CORRECT"
        else:
            segregation_status = "INCORRECT"

        db_audit = WasteAudit(
            user_id=audit_in.user_id,
            location_id=audit_in.location_id,
            bin_id=audit_in.bin_id,
            image_url=audit_in.image_url,
            waste_class=waste_class,
            waste_category=waste_category,
            confidence=audit_in.confidence,
            expected_bin=expected_bin,
            actual_bin=audit_in.actual_bin,
            segregation_status=segregation_status,
            model_name=audit_in.model_name or "VGG16_Custom",
            model_version=audit_in.model_version or "1.0.0",
            response_time_ms=audit_in.response_time_ms or 0.0,
            created_at=datetime.utcnow()
        )

        db.add(db_audit)
        db.commit()
        db.refresh(db_audit)

        return db_audit

    @staticmethod
    def get_audits(
        db: Session,
        limit: int = 50,
        offset: int = 0,
        location_id: Optional[int] = None,
        segregation_status: Optional[str] = None
    ):
        query = db.query(WasteAudit)
        if location_id:
            query = query.filter(WasteAudit.location_id == location_id)
        if segregation_status:
            query = query.filter(WasteAudit.segregation_status == segregation_status.upper())
        return query.order_by(WasteAudit.created_at.desc()).offset(offset).limit(limit).all()
