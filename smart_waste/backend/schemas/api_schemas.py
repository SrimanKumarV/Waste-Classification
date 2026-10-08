from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ClassificationResult(BaseModel):
    success: bool = True
    waste_class: str
    waste_category: str
    recommended_bin: str
    confidence: float
    is_confident: bool
    confidence_threshold: float
    model_name: str
    model_version: str
    inference_time_ms: float
    all_probabilities: Dict[str, float]
    explainability_url: Optional[str] = None
    warning: Optional[str] = None

class AuditCreate(BaseModel):
    waste_class: str
    actual_bin: str
    confidence: float
    location_id: int
    bin_id: Optional[str] = None
    user_id: Optional[int] = None
    image_url: Optional[str] = None
    model_name: Optional[str] = "VGG16_Custom"
    model_version: Optional[str] = "1.0.0"
    response_time_ms: Optional[float] = 0.0

class AuditResponse(BaseModel):
    id: int
    user_id: Optional[int]
    location_id: int
    location_name: Optional[str] = None
    bin_id: Optional[str]
    image_url: Optional[str]
    waste_class: str
    waste_category: str
    confidence: float
    expected_bin: str
    actual_bin: str
    segregation_status: str  # CORRECT, INCORRECT, UNCERTAIN
    model_name: str
    model_version: str
    response_time_ms: float
    created_at: datetime

    class Config:
        from_attributes = True

class SensorReadingCreate(BaseModel):
    bin_id: str
    fill_percentage: float = Field(..., ge=0.0, le=100.0)
    weight_kg: float = Field(..., ge=0.0)
    temperature: float = Field(default=25.0)
    gas_level: float = Field(default=50.0)
    device_id: Optional[str] = "ESP32-GATEWAY"

class SensorReadingResponse(BaseModel):
    id: int
    bin_id: str
    fill_percentage: float
    weight_kg: float
    temperature: float
    gas_level: float
    timestamp: datetime

    class Config:
        from_attributes = True

class BinResponse(BaseModel):
    id: str
    location_id: int
    location_name: Optional[str] = None
    bin_type: str
    capacity_kg: float
    status: str  # NORMAL, MODERATE, HIGH, CRITICAL
    fill_percentage: float
    weight_kg: float
    temperature: float
    gas_level: float
    last_updated: datetime

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    id: int
    location_id: Optional[int]
    location_name: Optional[str] = None
    priority: str
    title: str
    reason: str
    recommendation: str
    expected_benefit: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    audit_id: Optional[int] = None
    rating: int = Field(..., ge=1, le=5)
    feedback_type: str = "RECOMMENDATION_USEFULNESS"
    comments: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    audit_id: Optional[int]
    rating: int
    feedback_type: str
    comments: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    bin_id: str
    current_fill_percentage: float
    predicted_fill_4h: float
    predicted_fill_8h: float
    predicted_fill_24h: float
    expected_critical_time: Optional[str]
    hours_until_critical: Optional[float]
    model_evaluation: Dict[str, float]

class ModelMetricResponse(BaseModel):
    model_name: str
    model_version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    average_response_time_ms: float
    parameters: str
    is_active: bool

class EnergyAnalyticsResponse(BaseModel):
    traditional_trips_week: int
    optimized_trips_week: int
    trips_avoided_week: int
    fuel_saved_liters: float
    energy_saved_kwh: float
    co2_reduction_kg: float
    percent_reduction: float
    priority_collection_route: List[Dict[str, Any]]
    methodology: str
