"""
Image processing utilities for V-JEPA-2 deployment.
"""

import base64
import io
import logging
from typing import Optional, Tuple
from PIL import Image, ImageOps
import numpy as np

logger = logging.getLogger(__name__)


def base64_to_image(image_data: str) -> Image.Image:
    """
    Convert base64 image data to PIL Image.

    Args:
        image_data: Base64 encoded image data

    Returns:
        PIL Image object
    """
    try:
        # Remove data URL prefix if present
        if image_data.startswith("data:image"):
            image_data = image_data.split(",")[1]

        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        return image

    except Exception as e:
        logger.error(f"Failed to decode base64 image: {e}")
        raise


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    Convert PIL Image to base64 string.

    Args:
        image: PIL Image object
        format: Image format (PNG, JPEG, etc.)

    Returns:
        Base64 encoded image string
    """
    try:
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str

    except Exception as e:
        logger.error(f"Failed to encode image to base64: {e}")
        raise


def resize_image(
    image: Image.Image, size: Tuple[int, int], keep_aspect_ratio: bool = True
) -> Image.Image:
    """
    Resize image to specified dimensions.

    Args:
        image: PIL Image object
        size: Target size (width, height)
        keep_aspect_ratio: Whether to maintain aspect ratio

    Returns:
        Resized PIL Image
    """
    try:
        if keep_aspect_ratio:
            image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        else:
            image = image.resize(size, Image.Resampling.LANCZOS)

        return image

    except Exception as e:
        logger.error(f"Failed to resize image: {e}")
        raise


def normalize_image(image: Image.Image) -> np.ndarray:
    """
    Normalize image for model input.

    Args:
        image: PIL Image object

    Returns:
        Normalized numpy array
    """
    try:
        # Convert to numpy array
        image_array = np.array(image).astype(np.float32)

        # Normalize to [0, 1]
        image_array = image_array / 255.0

        return image_array

    except Exception as e:
        logger.error(f"Failed to normalize image: {e}")
        raise


def create_test_image(
    width: int = 256, height: int = 256, color: str = "red"
) -> Image.Image:
    """
    Create a test image for development and testing.

    Args:
        width: Image width
        height: Image height
        color: Image color

    Returns:
        PIL Image object
    """
    try:
        image = Image.new("RGB", (width, height), color=color)
        return image

    except Exception as e:
        logger.error(f"Failed to create test image: {e}")
        raise


def validate_image_format(image_data: str) -> bool:
    """
    Validate if the base64 image data is in a supported format.

    Args:
        image_data: Base64 encoded image data

    Returns:
        True if valid, False otherwise
    """
    try:
        image = base64_to_image(image_data)

        # Check if image can be processed
        image.verify()

        return True

    except Exception as e:
        logger.warning(f"Invalid image format: {e}")
        return False
