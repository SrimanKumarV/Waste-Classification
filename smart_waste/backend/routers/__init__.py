from .auth_router import auth_router
from .ml_router import ml_router
from .audit_router import audit_router
from .analytics_router import analytics_router
from .iot_router import iot_router
from .prediction_router import prediction_router
from .recommendation_router import recommendation_router
from .energy_router import energy_router
from .report_router import report_router

__all__ = [
    "auth_router", "ml_router", "audit_router", "analytics_router",
    "iot_router", "prediction_router", "recommendation_router",
    "energy_router", "report_router"
]
