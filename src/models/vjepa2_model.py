"""
V-JEPA-2 model implementation for visual intention analysis.
"""

import json
import os
from typing import Optional, Tuple, Dict, Any
import logging

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
import io
import base64
from transformers import AutoModel, AutoVideoProcessor

import src.datasets.utils.video.transforms as video_transforms
import src.datasets.utils.video.volume_transforms as volume_transforms
from src.models.vision_transformer import vit_giant_xformers_rope

logger = logging.getLogger(__name__)

IMAGENET_DEFAULT_MEAN = (0.485, 0.456, 0.406)
IMAGENET_DEFAULT_STD = (0.229, 0.224, 0.225)


class VJepa2Model:
    """
    V-JEPA-2 model wrapper for visual intention analysis.
    """

    def __init__(
        self,
        model_name: str = "facebook/vjepa2-vitg-fpc64-256",
        model_path: Optional[str] = None,
        device: str = "cuda",
    ):
        """
        Initialize the V-JEPA-2 model.

        Args:
            model_name: HuggingFace model name
            model_path: Path to local model weights
            device: Device to run inference on
        """
        self.model_name = model_name
        self.model_path = model_path
        self.device = device
        self.model_hf = None
        self.model_pt = None
        self.hf_transform = None
        self.pt_video_transform = None
        self.img_size = 256

        self._load_models()
        self._setup_transforms()

    def _load_models(self):
        """Load the HuggingFace and PyTorch models."""
        try:
            # Load HuggingFace model
            logger.info(f"Loading HuggingFace model: {self.model_name}")
            self.model_hf = AutoModel.from_pretrained(self.model_name)
            self.model_hf.to(self.device).eval()

            # Load PyTorch model if weights are provided
            if self.model_path and os.path.exists(self.model_path):
                logger.info(f"Loading PyTorch model from: {self.model_path}")
                self.model_pt = vit_giant_xformers_rope(
                    img_size=(self.img_size, self.img_size), num_frames=64
                )
                self.model_pt.to(self.device).eval()
                self._load_pretrained_weights(self.model_pt, self.model_path)
            else:
                logger.warning(
                    "PyTorch model weights not found, using HuggingFace model only"
                )

        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise

    def _load_pretrained_weights(self, model, pretrained_weights):
        """Load pretrained weights for the PyTorch model."""
        try:
            pretrained_dict = torch.load(
                pretrained_weights, weights_only=True, map_location="cpu"
            )["encoder"]
            pretrained_dict = {
                k.replace("module.", ""): v for k, v in pretrained_dict.items()
            }
            pretrained_dict = {
                k.replace("backbone.", ""): v for k, v in pretrained_dict.items()
            }
            msg = model.load_state_dict(pretrained_dict, strict=False)
            logger.info(f"Pretrained weights loaded with msg: {msg}")
        except Exception as e:
            logger.error(f"Failed to load pretrained weights: {e}")
            raise

    def _setup_transforms(self):
        """Setup video and image transforms."""
        try:
            # Setup HuggingFace transform
            self.hf_transform = AutoVideoProcessor.from_pretrained(self.model_name)
            self.img_size = self.hf_transform.crop_size["height"]

            # Setup PyTorch transform
            self.pt_video_transform = self._build_pt_video_transform(self.img_size)

        except Exception as e:
            logger.error(f"Failed to setup transforms: {e}")
            raise

    def _build_pt_video_transform(self, img_size):
        """Build PyTorch video transform."""
        short_side_size = int(256.0 / 224 * img_size)
        eval_transform = video_transforms.Compose(
            [
                video_transforms.Resize(short_side_size, interpolation="bilinear"),
                video_transforms.CenterCrop(size=(img_size, img_size)),
                volume_transforms.ClipToTensor(),
                video_transforms.Normalize(
                    mean=IMAGENET_DEFAULT_MEAN, std=IMAGENET_DEFAULT_STD
                ),
            ]
        )
        return eval_transform

    def _base64_to_image(self, image_data: str) -> Image.Image:
        """Convert base64 image data to PIL Image."""
        try:
            # Remove data URL prefix if present
            if image_data.startswith("data:image"):
                image_data = image_data.split(",")[1]

            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            return image
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {e}")
            raise

    def _image_to_video_tensor(self, image: Image.Image) -> torch.Tensor:
        """Convert single image to video tensor format."""
        # Convert PIL image to numpy array
        image_array = np.array(image)

        # Repeat the image to create a video-like tensor (T x H x W x C)
        video = np.stack([image_array] * 64, axis=0)  # 64 frames

        # Convert to torch tensor and permute to (T x C x H x W)
        video_tensor = torch.from_numpy(video).permute(0, 3, 1, 2)

        return video_tensor

    def analyze_image(
        self, image_data: str, goal_image: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an image for visual intention.

        Args:
            image_data: Base64 encoded image data
            goal_image: Optional base64 encoded goal image

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Convert base64 to image
            image = self._base64_to_image(image_data)

            # Convert to video tensor
            video_tensor = self._image_to_video_tensor(image)

            # Apply transforms
            x_pt = self.pt_video_transform(video_tensor).to(self.device).unsqueeze(0)
            x_hf = self.hf_transform(video_tensor, return_tensors="pt")[
                "pixel_values_videos"
            ].to(self.device)

            # Run inference
            with torch.inference_mode():
                if self.model_pt is not None:
                    out_patch_features_pt = self.model_pt(x_pt)
                    features = out_patch_features_pt
                else:
                    out_patch_features_hf = self.model_hf.get_vision_features(x_hf)
                    features = out_patch_features_hf

            # For now, return basic features
            # In a real implementation, you would pass these to a classifier
            result = {
                "features_shape": list(features.shape),
                "model_used": "pytorch" if self.model_pt is not None else "huggingface",
                "success": True,
            }

            return result

        except Exception as e:
            logger.error(f"Failed to analyze image: {e}")
            return {"error": str(e), "success": False}

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded models."""
        return {
            "model_name": self.model_name,
            "model_path": self.model_path,
            "device": self.device,
            "img_size": self.img_size,
            "pytorch_model_loaded": self.model_pt is not None,
            "huggingface_model_loaded": self.model_hf is not None,
        }
