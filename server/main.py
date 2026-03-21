from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import generate, health
from database import OUTPUT_DIR

app = FastAPI(
    title="Animated Explainer Studio — Backend",
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

app.mount("/files", StaticFiles(directory=OUTPUT_DIR), name="files")
