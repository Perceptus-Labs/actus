"""
API schemas for V-JEPA-2 deployment.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VJepa2Request(BaseModel):
    """Request schema for V-JEPA-2 analysis."""

    image_data: str = Field(..., description="Base64 encoded image data")
    goal_image: Optional[str] = Field(
        None, description="Optional base64 encoded goal image"
    )


class PredictionItem(BaseModel):
    """Individual prediction item."""

    action: str = Field(..., description="Predicted action name")
    confidence: float = Field(..., description="Confidence score (0-1)")
    class_id: int = Field(..., description="Class ID")


class VJepa2Response(BaseModel):
    """Response schema for V-JEPA-2 analysis."""

    predicted_action: str = Field(..., description="Top predicted action")
    confidence: float = Field(..., description="Confidence score (0-1)")
    has_intention: bool = Field(..., description="Whether there's a clear intention")
    intention_type: str = Field(..., description="Type of intention")
    description: str = Field(..., description="Description of the prediction")
    timestamp: datetime = Field(..., description="Timestamp of the analysis")
    top_predictions: Optional[List[PredictionItem]] = Field(
        None, description="Top-k predictions"
    )
    success: bool = Field(..., description="Whether the analysis was successful")
    error: Optional[str] = Field(None, description="Error message if failed")


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether the model is loaded")
    timestamp: datetime = Field(..., description="Current timestamp")
    model_info: Optional[Dict[str, Any]] = Field(None, description="Model information")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(..., description="Timestamp of the error")
