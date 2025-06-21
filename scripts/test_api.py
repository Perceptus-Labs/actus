#!/usr/bin/env python3
"""
Simple API test script for V-JEPA-2 deployment.
"""

import requests
import json
import base64
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.utils.image_processing import create_test_image, image_to_base64
except ImportError:
    # Fallback if dependencies are not available
    def create_test_image(width=256, height=256, color="red"):
        """Create a simple test image."""
        from PIL import Image

        return Image.new("RGB", (width, height), color=color)

    def image_to_base64(image, format="PNG"):
        """Convert image to base64."""
        import io

        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode()


def test_api_endpoints(base_url="http://localhost:8000"):
    """Test the API endpoints."""

    print(f"🧪 Testing API endpoints at {base_url}")
    print("=" * 50)

    # Test health endpoints
    print("\n1. Testing health endpoints...")

    try:
        # Root endpoint
        response = requests.get(f"{base_url}/")
        print(f"   Root endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data.get('message', 'N/A')}")

        # Health endpoint
        response = requests.get(f"{base_url}/health")
        print(f"   Health endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'N/A')}")

        # API health endpoint
        response = requests.get(f"{base_url}/api/v1/health")
        print(f"   API health endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Model loaded: {data.get('model_loaded', 'N/A')}")

    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to API server")
        print("   💡 Make sure the server is running: ./scripts/run_local.sh")
        return False

    # Test analysis endpoint
    print("\n2. Testing analysis endpoint...")

    try:
        # Create test image
        test_image = create_test_image(256, 256, "blue")
        image_base64 = image_to_base64(test_image)

        # Test with valid image
        payload = {"image_data": image_base64}

        response = requests.post(
            f"{base_url}/api/v1/analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        print(f"   Analysis endpoint: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   Predicted action: {data.get('predicted_action', 'N/A')}")
            print(f"   Confidence: {data.get('confidence', 'N/A')}")
            print(f"   Success: {data.get('success', 'N/A')}")
        elif response.status_code == 503:
            print("   ⚠️  Models not loaded (expected in development)")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")

        # Test with missing data
        response = requests.post(
            f"{base_url}/api/v1/analyze",
            json={},
            headers={"Content-Type": "application/json"},
        )
        print(f"   Missing data test: {response.status_code} (expected 422)")

    except Exception as e:
        print(f"   ❌ Error testing analysis endpoint: {e}")

    # Test model info endpoint
    print("\n3. Testing model info endpoint...")

    try:
        response = requests.get(f"{base_url}/api/v1/models/info")
        print(f"   Model info endpoint: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(
                f"   V-JEPA model loaded: {data.get('vjepa_model', {}).get('huggingface_model_loaded', 'N/A')}"
            )
            print(
                f"   Classifier loaded: {data.get('classifier', {}).get('classifier_loaded', 'N/A')}"
            )
        elif response.status_code == 503:
            print("   ⚠️  Models not loaded (expected in development)")

    except Exception as e:
        print(f"   ❌ Error testing model info endpoint: {e}")

    print("\n" + "=" * 50)
    print("✅ API testing completed!")

    return True


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Test V-JEPA-2 API endpoints")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API server (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    success = test_api_endpoints(args.url)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
