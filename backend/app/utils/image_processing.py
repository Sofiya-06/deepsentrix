"""Image pre-processing utilities."""

from __future__ import annotations

import os


def ensure_upload_dir(path: str) -> None:
    """Create the upload directory if it does not already exist."""
    os.makedirs(path, exist_ok=True)


def validate_image_extension(filename: str, allowed: list[str]) -> bool:
    """Return True if *filename* has an allowed extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in [e.lower() for e in allowed]


def validate_image_size(data: bytes, max_bytes: int) -> bool:
    """Return True if *data* is within the allowed size limit."""
    return len(data) <= max_bytes
