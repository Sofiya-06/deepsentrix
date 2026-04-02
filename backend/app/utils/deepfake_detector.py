"""
Thin convenience wrapper that lazily initialises the detector singleton.
"""

from __future__ import annotations

from app.config import settings
from app.models.detection import DeepfakeDetector, DetectionResult

_detector: DeepfakeDetector | None = None


def get_detector() -> DeepfakeDetector:
    global _detector  # noqa: PLW0603
    if _detector is None:
        _detector = DeepfakeDetector(model_path=settings.detection_model_path)
    return _detector


def analyze_image(image_data: bytes) -> DetectionResult:
    """Analyse *image_data* and return a detection result."""
    return get_detector().analyze(image_data)
