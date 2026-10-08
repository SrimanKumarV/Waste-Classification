import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base, SessionLocal
from .seed_data import seed_database
from .services.prediction_service import prediction_service
from .routers import (
    auth_router, ml_router, audit_router, analytics_router,
    iot_router, prediction_router, recommendation_router,
    energy_router, report_router
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB tables and demo dataset exist
    print("[App Startup] Initializing Smart Waste Segregation Analytics Platform...")
    Base.metadata.create_all(bind=engine)
    seed_database()

    # Train baseline prediction model
    db = SessionLocal()
    try:
        prediction_service.train_baseline_model(db)
        print("[App Startup] Predictive model baseline training complete.")
    finally:
        db.close()

    yield
    print("[App Shutdown] Shutting down application.")

app = FastAPI(
    title="Smart Waste Segregation Analytics",
    description="Intelligent Waste Auditing, IoT Monitoring, Predictive Analytics, and Decision Support Platform",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth_router)
app.include_router(ml_router)
app.include_router(audit_router)
app.include_router(analytics_router)
app.include_router(iot_router)
app.include_router(prediction_router)
app.include_router(recommendation_router)
app.include_router(energy_router)
app.include_router(report_router)

# Mount Static Files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Web Application Routes
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Smart Waste Segregation Analytics Dashboard</h1><p>Template loading...</p>")

@app.get("/mobile", response_class=HTMLResponse)
async def serve_mobile_app():
    mobile_file = TEMPLATES_DIR / "mobile.html"
    if mobile_file.exists():
        with open(mobile_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Mobile Scan Interface</h1>")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Smart Waste Segregation Analytics Platform",
        "version": "2.0.0"
    }
