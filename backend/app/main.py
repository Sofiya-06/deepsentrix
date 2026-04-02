from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.routes.api import router
from app.utils.image_processing import ensure_upload_dir

app = FastAPI(
    title=settings.app_name,
    description="Deepfake detection and pixel protection API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensure_upload_dir(settings.upload_dir)

if os.path.isdir(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {"message": "Deepsentrix API is running", "docs": "/docs"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
