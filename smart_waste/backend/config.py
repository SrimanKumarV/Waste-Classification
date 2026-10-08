import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'smart_waste.db'}")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "smart-waste-segregation-analytics-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ML Model Configuration
MODELS_DIR = WORKSPACE_DIR
DEFAULT_MODEL_NAME = "VGG16_Custom"
MODEL_CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))
INPUT_SIZE = (256, 256)

# 12 Waste Classes & Ordering
CLASS_NAMES = [
    "battery", "biological", "brown-glass", "cardboard", "clothes",
    "green-glass", "metal", "paper", "plastic", "shoes", "trash", "white-glass"
]

# Bin & Category Mappings
CLASS_CATEGORY_MAP = {
    "battery": "Hazardous",
    "biological": "Organic",
    "brown-glass": "Recyclable",
    "cardboard": "Recyclable",
    "clothes": "Recyclable",
    "green-glass": "Recyclable",
    "metal": "Recyclable",
    "paper": "Recyclable",
    "plastic": "Recyclable",
    "shoes": "Recyclable",
    "trash": "Organic",
    "white-glass": "Recyclable"
}

CATEGORY_BIN_MAP = {
    "Hazardous": "Hazardous (Red Bin)",
    "Organic": "Organic (Green Bin)",
    "Recyclable": "Recyclable (Blue Bin)"
}

CLASS_BIN_MAP = {
    cls: CATEGORY_BIN_MAP[CLASS_CATEGORY_MAP[cls]] for cls in CLASS_NAMES
}

BIN_COLORS = {
    "Hazardous (Red Bin)": "#ef4444",
    "Organic (Green Bin)": "#10b981",
    "Recyclable (Blue Bin)": "#3b82f6"
}

# IoT & Simulation Settings
SIMULATION_INTERVAL_SECONDS = 15
CRITICAL_FILL_THRESHOLD = 90.0
HIGH_FILL_THRESHOLD = 75.0
MODERATE_FILL_THRESHOLD = 50.0

# SDG 7 Energy Planning Baseline Parameters
TRADITIONAL_COLLECTION_TRIPS_PER_WEEK = 14  # 2 trips/day to all bins
AVERAGE_DISTANCE_PER_TRIP_KM = 12.5
AVERAGE_FUEL_CONSUMPTION_L_PER_KM = 0.28   # Light municipal diesel collection van
DIESEL_ENERGY_KWH_PER_LITER = 10.0
CO2_KG_PER_LITER_DIESEL = 2.68
