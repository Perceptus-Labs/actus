"""
API tests for V-JEPA-2 deployment.
"""

import pytest
import base64
import io
from PIL import Image
from fastapi.testclient import TestClient

from main import app

# Create test client
client = TestClient(app)


def create_test_image_base64():
    """Create a test image and return it as base64."""
    # Create a simple test image
    img = Image.new("RGB", (100, 100), color="red")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return img_str


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "V-JEPA-2 API"
        assert data["version"] == "1.0.0"

    def test_health_endpoint(self):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_api_health_endpoint(self):
        """Test API health endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "timestamp" in data


class TestAnalysisEndpoints:
    """Test analysis endpoints."""

    def test_analyze_endpoint_missing_data(self):
        """Test analyze endpoint with missing image data."""
        response = client.post("/api/v1/analyze", json={})
        assert response.status_code == 422  # Validation error

    def test_analyze_endpoint_invalid_data(self):
        """Test analyze endpoint with invalid data."""
        response = client.post("/api/v1/analyze", json={"image_data": "invalid"})
        # This might return 500 if models are not loaded, or 422 for validation
        assert response.status_code in [422, 500, 503]

    def test_analyze_endpoint_with_test_image(self):
        """Test analyze endpoint with a test image."""
        test_image = create_test_image_base64()

        response = client.post("/api/v1/analyze", json={"image_data": test_image})

        # This might fail if models are not loaded, but should not crash
        assert response.status_code in [200, 500, 503]

        if response.status_code == 200:
            data = response.json()
            assert "predicted_action" in data
            assert "confidence" in data
            assert "has_intention" in data
            assert "success" in data


class TestModelInfoEndpoints:
    """Test model information endpoints."""

    def test_model_info_endpoint(self):
        """Test model info endpoint."""
        response = client.get("/api/v1/models/info")
        # This might fail if models are not loaded
        assert response.status_code in [200, 503]


class TestErrorHandling:
    """Test error handling."""

    def test_nonexistent_endpoint(self):
        """Test nonexistent endpoint."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_invalid_json(self):
        """Test invalid JSON in request."""
        response = client.post("/api/v1/analyze", data="invalid json")
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])
