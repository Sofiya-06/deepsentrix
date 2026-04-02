"""
Deepfake detection model.

Uses a pre-trained ResNet50 backbone with a custom classification head.
Falls back to a heuristic analyser when no trained weights are available,
so the API works out-of-the-box without downloading large model files.
"""

from __future__ import annotations

import io
import logging
import os
from dataclasses import dataclass, field

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class DetectionResult:
    is_fake: bool
    confidence: float  # 0.0 – 1.0 (probability of being fake)
    detection_type: str  # "real" | "fake"
    details: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


class DeepfakeDetector:
    """Thin wrapper around a detection backbone."""

    TARGET_SIZE = (224, 224)

    def __init__(self, model_path: str | None = None):
        self._model = None
        self._model_path = model_path
        self._load_model()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_model(self) -> None:
        """Try to load a Keras / TF SavedModel; fall back to heuristic mode."""
        if not self._model_path or not os.path.exists(self._model_path):
            logger.info(
                "No model weights found at '%s'. Running in heuristic mode.",
                self._model_path,
            )
            return

        try:
            import tensorflow as tf  # type: ignore

            self._model = tf.keras.models.load_model(self._model_path)
            logger.info("Detection model loaded from %s", self._model_path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to load model: %s. Using heuristic mode.", exc)

    def _preprocess(self, image: Image.Image) -> np.ndarray:
        """Resize, convert to array and apply ImageNet normalisation."""
        img = image.convert("RGB").resize(self.TARGET_SIZE)
        arr = np.array(img, dtype=np.float32) / 255.0
        # ImageNet mean/std normalisation
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        arr = (arr - mean) / std
        return np.expand_dims(arr, axis=0)

    def _heuristic_analyze(self, image: Image.Image) -> float:
        """
        Simple heuristic that returns a fake-probability score based on
        noise patterns and colour statistics.  This is intentionally naive
        and is only used when no trained model is available.
        """
        img_array = np.array(image.convert("RGB"), dtype=np.float32)

        # 1. High-frequency noise estimate
        from PIL import ImageFilter

        blurred = np.array(image.convert("RGB").filter(ImageFilter.GaussianBlur(2)), dtype=np.float32)
        noise = np.abs(img_array - blurred)
        noise_score = float(np.mean(noise) / 255.0)

        # 2. Colour channel imbalance
        channel_means = img_array.mean(axis=(0, 1))
        channel_std = float(np.std(channel_means) / 255.0)

        # Combine scores (these weights are arbitrary stand-ins)
        score = min(1.0, noise_score * 3.0 + channel_std * 2.0)
        return score

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, image_data: bytes) -> DetectionResult:
        """Analyse raw image bytes and return a :class:`DetectionResult`."""
        image = Image.open(io.BytesIO(image_data))
        width, height = image.size

        if self._model is not None:
            arr = self._preprocess(image)
            prediction = self._model.predict(arr, verbose=0)
            fake_probability = float(prediction[0][0])
            method = "neural_network"
        else:
            fake_probability = self._heuristic_analyze(image)
            method = "heuristic"

        is_fake = fake_probability >= 0.5
        return DetectionResult(
            is_fake=is_fake,
            confidence=fake_probability if is_fake else 1.0 - fake_probability,
            detection_type="fake" if is_fake else "real",
            details={
                "method": method,
                "raw_score": round(fake_probability, 4),
                "image_size": {"width": width, "height": height},
            },
        )
