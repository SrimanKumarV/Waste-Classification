import random
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from .models.schemas import (
    User, Location, Bin, WasteAudit, SensorReading,
    Prediction, Recommendation, ModelMetric, UserFeedback
)
from .config import (
    CLASS_NAMES, CLASS_CATEGORY_MAP, CLASS_BIN_MAP,
    MODEL_CONFIDENCE_THRESHOLD
)

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def seed_database():
    """Initializes tables and populates with rich, consistent demonstration dataset."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Location).count() > 0:
            print("[SeedData] Database already seeded. Skipping initial seed.")
            return

        print("[SeedData] Seeding database with campus locations, bins, and 30-day history...")

        # 1. Users
        users_data = [
            User(name="Dr. S. K. Raman", email="admin@smartwaste.edu", password_hash=hash_pw("admin123"), role="ADMIN"),
            User(name="Ananya Sharma", email="auditor@smartwaste.edu", password_hash=hash_pw("audit123"), role="AUDITOR"),
            User(name="Rajesh Kumar", email="staff@smartwaste.edu", password_hash=hash_pw("staff123"), role="STAFF"),
            User(name="Campus Student", email="student@smartwaste.edu", password_hash=hash_pw("student123"), role="USER"),
        ]
        db.add_all(users_data)
        db.commit()

        # 2. Locations
        locations_data = [
            Location(name="Block A - Central Hall", description="Main Academic Complex & Faculty Offices", latitude=12.9716, longitude=80.2435),
            Location(name="Block B - Engineering Labs", description="Computer Science & Electronics Laboratories", latitude=12.9722, longitude=80.2440),
            Location(name="Block C - Central Library", description="University Library & Study Spaces", latitude=12.9719, longitude=80.2428),
            Location(name="Hostel Block A", description="Undergraduate Student Residential Complex", latitude=12.9730, longitude=80.2450),
            Location(name="Campus Food Court & Canteen", description="Central Dining and Cafeteria Hub", latitude=12.9710, longitude=80.2430),
        ]
        db.add_all(locations_data)
        db.commit()

        # 3. Bins
        bins_data = [
            Bin(id="BIN-001", location_id=1, bin_type="Recyclable (Blue Bin)", capacity_kg=30.0, fill_percentage=82.0, weight_kg=18.4, temperature=28.5, gas_level=62.0, status="HIGH"),
            Bin(id="BIN-002", location_id=1, bin_type="Organic (Green Bin)", capacity_kg=30.0, fill_percentage=48.0, weight_kg=14.2, temperature=30.1, gas_level=125.0, status="NORMAL"),
            Bin(id="BIN-003", location_id=5, bin_type="Organic (Green Bin)", capacity_kg=40.0, fill_percentage=94.0, weight_kg=36.8, temperature=33.2, gas_level=280.0, status="CRITICAL"),
            Bin(id="BIN-004", location_id=5, bin_type="Recyclable (Blue Bin)", capacity_kg=40.0, fill_percentage=76.0, weight_kg=15.1, temperature=29.0, gas_level=70.0, status="HIGH"),
            Bin(id="BIN-005", location_id=2, bin_type="Hazardous (Red Bin)", capacity_kg=20.0, fill_percentage=68.0, weight_kg=8.5, temperature=27.0, gas_level=40.0, status="MODERATE"),
            Bin(id="BIN-006", location_id=2, bin_type="Recyclable (Blue Bin)", capacity_kg=30.0, fill_percentage=42.0, weight_kg=7.8, temperature=27.4, gas_level=55.0, status="NORMAL"),
            Bin(id="BIN-007", location_id=4, bin_type="Recyclable (Blue Bin)", capacity_kg=35.0, fill_percentage=88.0, weight_kg=21.0, temperature=28.8, gas_level=65.0, status="HIGH"),
            Bin(id="BIN-008", location_id=3, bin_type="Recyclable (Blue Bin)", capacity_kg=25.0, fill_percentage=35.0, weight_kg=6.2, temperature=26.0, gas_level=35.0, status="NORMAL"),
        ]
        db.add_all(bins_data)
        db.commit()

        # 4. Model Metrics (Real experimental notebook results)
        metrics_data = [
            ModelMetric(model_name="VGG16 (Transfer Learning)", model_version="1.0.0", accuracy=0.8913, precision=0.8900, recall=0.8800, f1_score=0.8800, mae=None, rmse=None, average_response_time_ms=145.2, parameters="14.7M", is_active=True),
            ModelMetric(model_name="Custom CNN (6-Layer)", model_version="1.0.0", accuracy=0.8613, precision=0.8520, recall=0.8410, f1_score=0.8460, mae=None, rmse=None, average_response_time_ms=92.4, parameters="8.4M", is_active=False),
            ModelMetric(model_name="ResNet50 Residual", model_version="1.0.0", accuracy=0.5340, precision=0.5210, recall=0.5050, f1_score=0.5120, mae=None, rmse=None, average_response_time_ms=118.5, parameters="23.5M", is_active=False),
            ModelMetric(model_name="MobileNetV3-Small (Edge)", model_version="1.0.0", accuracy=0.5776, precision=0.5640, recall=0.5510, f1_score=0.5570, mae=None, rmse=None, average_response_time_ms=42.1, parameters="2.9M", is_active=False),
            ModelMetric(model_name="RandomForest Time-Series Fill Regressor", model_version="1.2.0", accuracy=None, precision=None, recall=None, f1_score=None, mae=3.84, rmse=5.12, average_response_time_ms=12.0, parameters="50 Estimators", is_active=True),
        ]
        db.add_all(metrics_data)
        db.commit()

        # 5. Historical Sensor Readings (Last 30 Days)
        print("[SeedData] Generating 30 days of realistic IoT sensor readings...")
        now = datetime.utcnow()
        sensor_readings = []

        for b in bins_data:
            curr_fill = 20.0
            # Step every 6 hours over 30 days = 120 points per bin
            for step in range(120, 0, -1):
                timestamp = now - timedelta(hours=step * 6)
                hour = timestamp.hour
                
                # Diurnal growth rate
                rate = 4.0 if 12 <= hour <= 18 else (2.0 if 8 <= hour <= 12 else 0.5)
                curr_fill += rate + random.uniform(-1.0, 2.0)
                if curr_fill >= 96.0:
                    curr_fill = random.uniform(4.0, 10.0)  # Emptied

                density = 0.22 if "Organic" in b.bin_type else 0.16
                wt = max(0.5, curr_fill * density + random.uniform(-0.2, 0.2))
                temp = 27.0 + random.uniform(-2.0, 4.0)
                gas = (140.0 if "Organic" in b.bin_type else 45.0) + (curr_fill * 1.2) + random.uniform(-5.0, 5.0)

                sensor_readings.append(SensorReading(
                    bin_id=b.id,
                    fill_percentage=round(curr_fill, 1),
                    weight_kg=round(wt, 2),
                    temperature=round(temp, 1),
                    gas_level=round(gas, 1),
                    timestamp=timestamp
                ))

        db.bulk_save_objects(sensor_readings)
        db.commit()

        # 6. Historical Waste Audits (520+ records over 30 days across 5 locations)
        print("[SeedData] Generating 520+ consistent waste audit records...")
        audits = []
        feedbacks = []

        # Location behavior profiles:
        # Block A: 91% correct (good adherence)
        # Block B: 68% correct (lab confusion)
        # Block C: 82% correct (library)
        # Hostel A: 58% correct (moderate student carelessness)
        # Canteen: 49% correct (fast-food rush hour contamination)
        loc_compliance = {1: 0.91, 2: 0.68, 3: 0.82, 4: 0.58, 5: 0.49}

        bin_options = ["Recyclable (Blue Bin)", "Organic (Green Bin)", "Hazardous (Red Bin)"]

        for i in range(530):
            # Spread across 30 days
            delta_hours = random.uniform(1.0, 30.0 * 24.0)
            audit_time = now - timedelta(hours=delta_hours)

            loc_id = random.choices([1, 2, 3, 4, 5], weights=[22, 20, 15, 23, 20])[0]
            waste_cls = random.choice(CLASS_NAMES)
            expected_bin = CLASS_BIN_MAP[waste_cls]
            waste_cat = CLASS_CATEGORY_MAP[waste_cls]

            # Determine whether user segregated correctly based on location profile
            p_correct = loc_compliance[loc_id]
            is_correct = random.random() < p_correct

            conf = round(random.uniform(0.78, 0.98), 4)

            if is_correct:
                actual_bin = expected_bin
                status = "CORRECT"
            else:
                wrong_choices = [b for b in bin_options if b != expected_bin]
                actual_bin = random.choice(wrong_choices)
                status = "INCORRECT"

            assigned_bin = random.choice([b.id for b in bins_data if b.location_id == loc_id])

            audit_item = WasteAudit(
                user_id=random.choice([1, 2, 3, 4]),
                location_id=loc_id,
                bin_id=assigned_bin,
                image_url=None,
                waste_class=waste_cls,
                waste_category=waste_cat,
                confidence=conf,
                expected_bin=expected_bin,
                actual_bin=actual_bin,
                segregation_status=status,
                model_name="VGG16 (Transfer Learning)",
                model_version="1.0.0",
                response_time_ms=round(random.uniform(110.0, 185.0), 1),
                created_at=audit_time
            )
            db.add(audit_item)
            audits.append(audit_item)

        db.commit()

        # 7. Initial Seed Recommendations
        recs = [
            Recommendation(
                location_id=5,
                priority="CRITICAL",
                title="Immediate Collection Required: BIN-003",
                reason="BIN-003 (Organic) in Campus Food Court reached 94% capacity. Gas emissions rising rapidly (280 ppm).",
                recommendation="Dispatch janitorial team to empty BIN-003 within 30 minutes to avoid overflow and odor.",
                expected_benefit="Prevents dining area odor complaints and public health contamination.",
                status="ACTIVE",
                created_at=now - timedelta(minutes=45)
            ),
            Recommendation(
                location_id=5,
                priority="HIGH",
                title="Conduct Source Segregation Awareness at Campus Food Court",
                reason="Food Court segregation efficiency dropped to 49.0% over the last 7 days. Plastic cups/wrappers frequently discarded into green organic bins.",
                recommendation="Install prominent pictorial signage at disposal stations and deploy staff monitoring during peak lunch hours (12:30 PM - 2:00 PM).",
                expected_benefit="Expected to improve source segregation by 22% and eliminate organic waste contamination.",
                status="ACTIVE",
                created_at=now - timedelta(hours=2)
            ),
            Recommendation(
                location_id=2,
                priority="HIGH",
                title="Address Electronic/Lab Waste Contamination in Block B",
                reason="Detected lab batteries and wire components improperly mixed into general blue recyclable bins.",
                recommendation="Install dedicated Hazardous Red e-waste collection bins directly inside CS & Electronics labs.",
                expected_benefit="Protects recycling batches and eliminates chemical contamination risks.",
                status="ACTIVE",
                created_at=now - timedelta(hours=6)
            ),
            Recommendation(
                location_id=4,
                priority="MEDIUM",
                title="Review Bin Placement in Hostel Block A",
                reason="Hostel Block A segregation efficiency stands at 58.2%. High volume of cardboard and food packaging.",
                recommendation="Increase frequency of recycling bin collection from 2x to 3x weekly and host hostel floor awareness challenge.",
                expected_benefit="Increases recyclable recovery by 15% and avoids bin overflow on weekends.",
                status="ACTIVE",
                created_at=now - timedelta(days=1)
            )
        ]
        db.add_all(recs)
        db.commit()

        # 8. User feedback samples
        feedbacks = [
            UserFeedback(rating=5, feedback_type="RECOMMENDATION_USEFULNESS", comments="Clear bin suggestion saved time sorting cafeteria plastic.", created_at=now - timedelta(hours=3)),
            UserFeedback(rating=4, feedback_type="RECOMMENDATION_USEFULNESS", comments="Very fast classification, Grad-CAM visual is very educational.", created_at=now - timedelta(hours=7)),
            UserFeedback(rating=5, feedback_type="SYSTEM_EVALUATION", comments="Great IoT live fill-level tracking on mobile view.", created_at=now - timedelta(hours=14)),
        ]
        db.add_all(feedbacks)
        db.commit()

        print("[SeedData] Successfully seeded database with 520+ audits and 960+ sensor points!")

    except Exception as e:
        print(f"[SeedData] Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
