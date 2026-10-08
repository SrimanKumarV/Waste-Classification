from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from ..services.ml_service import MLService, registry
from ..config import MODEL_CONFIDENCE_THRESHOLD

ml_router = APIRouter(prefix="/api", tags=["Machine Learning"])

class SetModelRequest(BaseModel):
    model_key: str

@ml_router.post("/waste/predict")
async def predict_waste(
    file: UploadFile = File(...),
    confidence_threshold: float = Query(MODEL_CONFIDENCE_THRESHOLD),
    generate_explainability: bool = Query(True)
):
    """
    Classifies uploaded waste image into one of 12 categories,
    computes confidence score, checks uncertainty threshold,
    and maps to appropriate dustbin with Grad-CAM heatmap.
    """
    is_image = (
        (file.content_type and file.content_type.startswith("image/")) or
        (file.filename and file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")))
    )
    if not is_image:
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image (.jpg, .png, etc.).")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    result = MLService.classify_image(
        image_bytes=content,
        confidence_threshold=confidence_threshold,
        generate_explainability=generate_explainability
    )
    return result

@ml_router.get("/models")
def list_models():
    """Returns the Model Registry and multi-model benchmark evaluation table."""
    return {
        "active_model": registry.active_model_key,
        "models": registry.get_available_models()
    }

@ml_router.post("/models/active")
def set_active_model(req: SetModelRequest):
    """Switches the active inference model in the registry."""
    success = registry.set_active_model(req.model_key)
    if not success:
        raise HTTPException(status_code=404, detail=f"Model key '{req.model_key}' not found.")
    return {
        "success": True,
        "active_model": registry.active_model_key,
        "message": f"Successfully activated {req.model_key}"
    }
