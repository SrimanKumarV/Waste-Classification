import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smart_waste.backend.database import Base
from smart_waste.backend.models.schemas import Location, WasteAudit
from smart_waste.backend.services.audit_service import AuditService
from smart_waste.backend.schemas.api_schemas import AuditCreate

class TestAuditService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Seed sample location
        loc = Location(name="Test Academic Block", description="Testing")
        self.db.add(loc)
        self.db.commit()
        self.loc_id = loc.id

    def tearDown(self):
        self.db.close()

    def test_correct_segregation(self):
        """Plastic placed into Blue Bin must evaluate to CORRECT."""
        audit_in = AuditCreate(
            waste_class="plastic",
            actual_bin="Recyclable (Blue Bin)",
            confidence=0.95,
            location_id=self.loc_id
        )
        audit = AuditService.create_audit(self.db, audit_in)
        self.assertEqual(audit.expected_bin, "Recyclable (Blue Bin)")
        self.assertEqual(audit.segregation_status, "CORRECT")

    def test_incorrect_segregation_contamination(self):
        """Plastic placed into Green Bin must evaluate to INCORRECT."""
        audit_in = AuditCreate(
            waste_class="plastic",
            actual_bin="Organic (Green Bin)",
            confidence=0.92,
            location_id=self.loc_id
        )
        audit = AuditService.create_audit(self.db, audit_in)
        self.assertEqual(audit.expected_bin, "Recyclable (Blue Bin)")
        self.assertEqual(audit.segregation_status, "INCORRECT")

    def test_uncertain_classification(self):
        """Confidence below threshold must evaluate to UNCERTAIN."""
        audit_in = AuditCreate(
            waste_class="paper",
            actual_bin="Recyclable (Blue Bin)",
            confidence=0.55,  # Below 0.70 threshold
            location_id=self.loc_id
        )
        audit = AuditService.create_audit(self.db, audit_in)
        self.assertEqual(audit.segregation_status, "UNCERTAIN")

if __name__ == "__main__":
    unittest.main()
