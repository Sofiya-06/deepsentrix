import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Deepsentrix API"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    api_prefix: str = "/api"

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]

    # Upload settings
    max_upload_size: int = 10 * 1024 * 1024  # 10 MB
    allowed_extensions: list[str] = ["jpg", "jpeg", "png", "webp"]

    # Model settings
    model_confidence_threshold: float = 0.5
    detection_model_path: str = os.getenv("DETECTION_MODEL_PATH", "models/deepfake_detector.h5")

    # Storage
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    results_db: str = os.getenv("RESULTS_DB", "deepsentrix.db")

    class Config:
        env_file = ".env"


settings = Settings()
