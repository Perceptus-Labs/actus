"""
V-JEPA-2 classifier for action prediction.
"""

import json
import os
from typing import Dict, Any, List, Optional
import logging

import torch
import torch.nn.functional as F
from src.models.attentive_pooler import AttentiveClassifier

logger = logging.getLogger(__name__)


class VJepa2Classifier:
    """
    V-JEPA-2 classifier for predicting actions from visual features.
    """

    def __init__(
        self,
        classifier_path: Optional[str] = None,
        embed_dim: int = 1408,
        num_classes: int = 174,
        device: str = "cuda",
    ):
        """
        Initialize the V-JEPA-2 classifier.

        Args:
            classifier_path: Path to classifier weights
            embed_dim: Embedding dimension
            num_classes: Number of action classes
            device: Device to run inference on
        """
        self.classifier_path = classifier_path
        self.embed_dim = embed_dim
        self.num_classes = num_classes
        self.device = device
        self.classifier = None
        self.class_names = {}

        self._load_classifier()
        self._load_class_names()

    def _load_classifier(self):
        """Load the classifier model."""
        try:
            self.classifier = (
                AttentiveClassifier(
                    embed_dim=self.embed_dim,
                    num_heads=16,
                    depth=4,
                    num_classes=self.num_classes,
                )
                .to(self.device)
                .eval()
            )

            if self.classifier_path and os.path.exists(self.classifier_path):
                logger.info(f"Loading classifier weights from: {self.classifier_path}")
                self._load_classifier_weights(self.classifier, self.classifier_path)
            else:
                logger.warning(
                    "Classifier weights not found, using random initialization"
                )

        except Exception as e:
            logger.error(f"Failed to load classifier: {e}")
            raise

    def _load_classifier_weights(self, model, pretrained_weights):
        """Load pretrained weights for the classifier."""
        try:
            pretrained_dict = torch.load(
                pretrained_weights, weights_only=True, map_location="cpu"
            )["classifiers"][0]
            pretrained_dict = {
                k.replace("module.", ""): v for k, v in pretrained_dict.items()
            }
            msg = model.load_state_dict(pretrained_dict, strict=False)
            logger.info(f"Classifier weights loaded with msg: {msg}")
        except Exception as e:
            logger.error(f"Failed to load classifier weights: {e}")
            raise

    def _load_class_names(self):
        """Load class names for action prediction."""
        try:
            # Try to load from local file first
            ssv2_classes_path = "ssv2_classes.json"
            if os.path.exists(ssv2_classes_path):
                with open(ssv2_classes_path, "r") as f:
                    self.class_names = json.load(f)
                logger.info(
                    f"Loaded {len(self.class_names)} class names from local file"
                )
            else:
                # Use default class names or download them
                logger.warning("Class names file not found, using default mapping")
                self.class_names = {
                    str(i): f"action_{i}" for i in range(self.num_classes)
                }

        except Exception as e:
            logger.error(f"Failed to load class names: {e}")
            self.class_names = {str(i): f"action_{i}" for i in range(self.num_classes)}

    def predict_actions(self, features: torch.Tensor, top_k: int = 5) -> Dict[str, Any]:
        """
        Predict actions from visual features.

        Args:
            features: Visual features tensor
            top_k: Number of top predictions to return

        Returns:
            Dictionary containing prediction results
        """
        try:
            if self.classifier is None:
                raise ValueError("Classifier not loaded")

            with torch.inference_mode():
                # Get classifier output
                logits = self.classifier(features)

                # Get top-k predictions
                top_k_values, top_k_indices = logits.topk(top_k, dim=-1)
                top_k_probs = F.softmax(top_k_values, dim=-1)

                # Convert to list format
                predictions = []
                for i in range(top_k):
                    idx = top_k_indices[0, i].item()
                    prob = top_k_probs[0, i].item()
                    class_name = self.class_names.get(str(idx), f"action_{idx}")

                    predictions.append(
                        {"action": class_name, "confidence": prob, "class_id": idx}
                    )

                # Get the top prediction
                top_prediction = predictions[0]

                result = {
                    "predicted_action": top_prediction["action"],
                    "confidence": top_prediction["confidence"],
                    "has_intention": top_prediction["confidence"] > 0.5,
                    "intention_type": "visual_action",
                    "description": f"V-JEPA-2 predicted action: {top_prediction['action']}",
                    "top_predictions": predictions,
                    "success": True,
                }

                return result

        except Exception as e:
            logger.error(f"Failed to predict actions: {e}")
            return {"error": str(e), "success": False}

    def get_classifier_info(self) -> Dict[str, Any]:
        """Get information about the classifier."""
        return {
            "classifier_path": self.classifier_path,
            "embed_dim": self.embed_dim,
            "num_classes": self.num_classes,
            "device": self.device,
            "classifier_loaded": self.classifier is not None,
            "num_class_names": len(self.class_names),
        }
