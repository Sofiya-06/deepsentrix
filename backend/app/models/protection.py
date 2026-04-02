"""
Pixel protection module.

Applies various obfuscation techniques to an image so that deepfake
artifacts cannot be reverse-engineered, while still communicating to
a viewer that the content has been tampered with.
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class ProtectionResult:
    protected_image: bytes  # JPEG/PNG bytes
    technique: str
    protection_level: str  # "low" | "medium" | "high"
    details: dict


class PixelProtector:
    """Apply pixel-level protection to images detected as deepfakes."""

    # Pixel block sizes for the pixelation technique
    PIXEL_SIZES = {"low": 10, "medium": 20, "high": 40}

    # Blur kernel sizes
    BLUR_KERNELS = {"low": (15, 15), "medium": (31, 31), "high": (61, 61)}

    def protect(
        self,
        image_data: bytes,
        technique: str = "pixelate",
        level: str = "medium",
    ) -> ProtectionResult:
        """
        Apply *technique* at *level* intensity.

        Parameters
        ----------
        image_data: raw image bytes
        technique: "pixelate" | "blur" | "noise" | "combined"
        level: "low" | "medium" | "high"
        """
        if level not in ("low", "medium", "high"):
            level = "medium"

        image = Image.open(io.BytesIO(image_data)).convert("RGB")

        technique_map = {
            "pixelate": self._pixelate,
            "blur": self._blur,
            "noise": self._add_noise,
            "combined": self._combined,
        }
        func = technique_map.get(technique, self._pixelate)
        protected_image, details = func(image, level)

        output = io.BytesIO()
        protected_image.save(output, format="JPEG", quality=90)
        return ProtectionResult(
            protected_image=output.getvalue(),
            technique=technique,
            protection_level=level,
            details=details,
        )

    # ------------------------------------------------------------------
    # Techniques
    # ------------------------------------------------------------------

    def _pixelate(self, image: Image.Image, level: str) -> tuple[Image.Image, dict]:
        pixel_size = self.PIXEL_SIZES[level]
        width, height = image.size
        small = image.resize(
            (max(1, width // pixel_size), max(1, height // pixel_size)),
            resample=Image.NEAREST,
        )
        result = small.resize((width, height), resample=Image.NEAREST)
        return result, {"pixel_size": pixel_size}

    def _blur(self, image: Image.Image, level: str) -> tuple[Image.Image, dict]:
        kernel = self.BLUR_KERNELS[level]
        cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        blurred = cv2.GaussianBlur(cv_img, kernel, 0)
        result = Image.fromarray(cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB))
        return result, {"kernel_size": kernel}

    def _add_noise(self, image: Image.Image, level: str) -> tuple[Image.Image, dict]:
        intensities = {"low": 15, "medium": 40, "high": 80}
        intensity = intensities[level]
        arr = np.array(image, dtype=np.int16)
        noise = np.random.randint(-intensity, intensity + 1, arr.shape, dtype=np.int16)
        noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy), {"noise_intensity": intensity}

    def _combined(self, image: Image.Image, level: str) -> tuple[Image.Image, dict]:
        # Apply pixelation then light noise on top
        pixelated, pix_details = self._pixelate(image, level)
        final, noise_details = self._add_noise(pixelated, "low")
        return final, {**pix_details, **noise_details, "techniques": ["pixelate", "noise"]}
