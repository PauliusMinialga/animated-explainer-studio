from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from routers import generate, videos, health
from database import OUTPUT_DIR

app = FastAPI(
    title="Animated Explainer Studio — Backend",
    description="Turn any topic or code snippet into an animated, avatar-narrated video lesson.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(generate.router)
app.include_router(videos.router)

# Serve generated video files at /files/{job_id}/animation.mp4 etc.
app.mount("/files", StaticFiles(directory=OUTPUT_DIR), name="files")
