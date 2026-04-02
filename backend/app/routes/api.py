"""API routes for deepfake detection and pixel protection."""

from __future__ import annotations

import base64
import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config import settings
from app.models.protection import PixelProtector
from app.utils.deepfake_detector import analyze_image
from app.utils.image_processing import validate_image_extension, validate_image_size

logger = logging.getLogger(__name__)
router = APIRouter()
protector = PixelProtector()


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _get_db():
    conn = sqlite3.connect(settings.results_db)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS results (
            id          TEXT PRIMARY KEY,
            filename    TEXT,
            is_fake     INTEGER,
            confidence  REAL,
            detection_type TEXT,
            details     TEXT,
            created_at  TEXT
        )
        """
    )
    conn.commit()
    return conn


def _save_result(result_id: str, filename: str, detection) -> None:
    conn = _get_db()
    conn.execute(
        "INSERT INTO results VALUES (?,?,?,?,?,?,?)",
        (
            result_id,
            filename,
            int(detection.is_fake),
            detection.confidence,
            detection.detection_type,
            json.dumps(detection.details),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class AnalysisResponse(BaseModel):
    result_id: str
    filename: str
    is_fake: bool
    confidence: float
    detection_type: str
    details: dict
    protected_image: Optional[str] = None  # base64-encoded if fake
    protection_technique: Optional[str] = None
    created_at: str


class ResultResponse(BaseModel):
    result_id: str
    filename: str
    is_fake: bool
    confidence: float
    detection_type: str
    details: dict
    created_at: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    file: UploadFile = File(...),
    protection_technique: str = Form("pixelate"),
    protection_level: str = Form("medium"),
):
    """Upload an image, detect deepfakes, and optionally protect it."""
    if not validate_image_extension(file.filename or "", settings.allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {settings.allowed_extensions}",
        )

    image_data = await file.read()
    if not validate_image_size(image_data, settings.max_upload_size):
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_upload_size // (1024*1024)} MB",
        )

    try:
        detection = analyze_image(image_data)
    except Exception as exc:
        logger.exception("Detection failed")
        raise HTTPException(status_code=500, detail="Detection failed") from exc

    result_id = str(uuid.uuid4())
    _save_result(result_id, file.filename or "unknown", detection)

    protected_b64: Optional[str] = None
    technique_used: Optional[str] = None

    if detection.is_fake:
        try:
            protection = protector.protect(image_data, technique=protection_technique, level=protection_level)
            protected_b64 = base64.b64encode(protection.protected_image).decode("utf-8")
            technique_used = protection.technique
        except Exception as exc:
            logger.exception("Protection failed")
            # Non-fatal: return detection result without protection
            protected_b64 = None

    return AnalysisResponse(
        result_id=result_id,
        filename=file.filename or "unknown",
        is_fake=detection.is_fake,
        confidence=round(detection.confidence, 4),
        detection_type=detection.detection_type,
        details=detection.details,
        protected_image=protected_b64,
        protection_technique=technique_used,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/protect")
async def protect_image(
    file: UploadFile = File(...),
    technique: str = Form("pixelate"),
    level: str = Form("medium"),
):
    """Apply pixel protection to any uploaded image (regardless of detection)."""
    if not validate_image_extension(file.filename or "", settings.allowed_extensions):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    image_data = await file.read()
    if not validate_image_size(image_data, settings.max_upload_size):
        raise HTTPException(status_code=413, detail="File too large")

    try:
        result = protector.protect(image_data, technique=technique, level=level)
    except Exception as exc:
        logger.exception("Protection failed")
        raise HTTPException(status_code=500, detail="Protection failed") from exc

    protected_b64 = base64.b64encode(result.protected_image).decode("utf-8")
    return JSONResponse(
        content={
            "protected_image": protected_b64,
            "technique": result.technique,
            "protection_level": result.protection_level,
            "details": result.details,
        }
    )


@router.get("/results/{result_id}", response_model=ResultResponse)
async def get_result(result_id: str):
    """Retrieve a previously stored analysis result by ID."""
    conn = _get_db()
    row = conn.execute("SELECT * FROM results WHERE id = ?", (result_id,)).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Result not found")

    return ResultResponse(
        result_id=row["id"],
        filename=row["filename"],
        is_fake=bool(row["is_fake"]),
        confidence=row["confidence"],
        detection_type=row["detection_type"],
        details=json.loads(row["details"]),
        created_at=row["created_at"],
    )


@router.get("/results")
async def list_results(limit: int = 20):
    """List the most recent analysis results."""
    conn = _get_db()
    rows = conn.execute(
        "SELECT * FROM results ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()

    return [
        {
            "result_id": r["id"],
            "filename": r["filename"],
            "is_fake": bool(r["is_fake"]),
            "confidence": r["confidence"],
            "detection_type": r["detection_type"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]
