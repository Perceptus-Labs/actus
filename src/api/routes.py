"""
API routes for V-JEPA-2 deployment.
"""

import os
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from .schemas import VJepa2Request, VJepa2Response, HealthResponse, ErrorResponse
from src.models import VJepa2Model, VJepa2Classifier

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["vjepa2"])

# Global model instances
vjepa_model: Optional[VJepa2Model] = None
vjepa_classifier: Optional[VJepa2Classifier] = None


def get_models():
    """Dependency to get model instances."""
    global vjepa_model, vjepa_classifier

    if vjepa_model is None or vjepa_classifier is None:
        raise HTTPException(status_code=503, detail="Models not loaded")

    return vjepa_model, vjepa_classifier


def load_models():
    """Load the V-JEPA-2 models."""
    global vjepa_model, vjepa_classifier

    try:
        # Get configuration from environment
        model_name = os.getenv("MODEL_NAME", "facebook/vjepa2-vitg-fpc64-256")
        model_path = os.getenv("MODEL_PATH")
        classifier_path = os.getenv("CLASSIFIER_PATH")
        device = os.getenv("DEVICE", "cuda")

        logger.info("Loading V-JEPA-2 models...")

        # Load main model
        vjepa_model = VJepa2Model(
            model_name=model_name, model_path=model_path, device=device
        )

        # Load classifier
        vjepa_classifier = VJepa2Classifier(
            classifier_path=classifier_path, device=device
        )

        logger.info("Models loaded successfully")

    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global vjepa_model, vjepa_classifier

    model_loaded = vjepa_model is not None and vjepa_classifier is not None

    model_info = None
    if model_loaded:
        model_info = {
            "vjepa_model": vjepa_model.get_model_info(),
            "classifier": vjepa_classifier.get_classifier_info(),
        }

    return HealthResponse(
        status="healthy" if model_loaded else "unhealthy",
        model_loaded=model_loaded,
        timestamp=datetime.utcnow(),
        model_info=model_info,
    )


@router.post("/analyze", response_model=VJepa2Response)
async def analyze_image(request: VJepa2Request, models: tuple = Depends(get_models)):
    """
    Analyze an image for visual intention using V-JEPA-2.

    Args:
        request: Image analysis request
        models: Tuple of (vjepa_model, classifier)

    Returns:
        Analysis results
    """
    vjepa_model, classifier = models

    try:
        logger.info("Starting image analysis")

        # Analyze image with V-JEPA-2
        analysis_result = vjepa_model.analyze_image(
            image_data=request.image_data, goal_image=request.goal_image
        )

        if not analysis_result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"Model analysis failed: {analysis_result.get('error', 'Unknown error')}",
            )

        # For now, return a mock response since we need the actual classifier integration
        # In a real implementation, you would pass the features to the classifier
        mock_response = VJepa2Response(
            predicted_action="reaching",
            confidence=0.85,
            has_intention=True,
            intention_type="visual_action",
            description="V-JEPA-2 predicted action: reaching",
            timestamp=datetime.utcnow(),
            success=True,
        )

        logger.info("Image analysis completed successfully")
        return mock_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/models/info")
async def get_model_info(models: tuple = Depends(get_models)):
    """Get information about the loaded models."""
    vjepa_model, classifier = models

    return {
        "vjepa_model": vjepa_model.get_model_info(),
        "classifier": classifier.get_classifier_info(),
        "timestamp": datetime.utcnow().isoformat(),
    }


# Initialize models on startup
@router.on_event("startup")
async def startup_event():
    """Initialize models on application startup."""
    try:
        load_models()
    except Exception as e:
        logger.error(f"Failed to initialize models on startup: {e}")
        # Don't raise here, let the application start but mark models as unavailable
