import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smart_waste.backend.database import Base
from smart_waste.backend.models.schemas import Location, WasteAudit
from smart_waste.backend.services.analytics_service import AnalyticsService

class TestAnalyticsService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Seed location
        loc = Location(name="Test Canteen")
        self.db.add(loc)
        self.db.commit()

        # Seed 10 audits: 7 correct, 3 incorrect -> Expected efficiency = 70.0%
        now = datetime.utcnow()
        for i in range(7):
            self.db.add(WasteAudit(
                location_id=loc.id,
                waste_class="plastic",
                waste_category="Recyclable",
                confidence=0.9,
                expected_bin="Recyclable (Blue Bin)",
                actual_bin="Recyclable (Blue Bin)",
                segregation_status="CORRECT",
                created_at=now
            ))
        for i in range(3):
            self.db.add(WasteAudit(
                location_id=loc.id,
                waste_class="plastic",
                waste_category="Recyclable",
                confidence=0.9,
                expected_bin="Recyclable (Blue Bin)",
                actual_bin="Organic (Green Bin)",
                segregation_status="INCORRECT",
                created_at=now
            ))
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_segregation_efficiency_calculation(self):
        kpis = AnalyticsService.get_overview_kpis(self.db, days=30)
        self.assertEqual(kpis["total_audits"], 10)
        self.assertEqual(kpis["correct_count"], 7)
        self.assertEqual(kpis["incorrect_count"], 3)
        self.assertEqual(kpis["segregation_efficiency_pct"], 70.0)
        self.assertEqual(kpis["contamination_rate_pct"], 30.0)

if __name__ == "__main__":
    unittest.main()
