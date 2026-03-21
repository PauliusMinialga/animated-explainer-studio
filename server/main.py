from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import generate, videos, health

app = FastAPI(
    title="Animated Explainer Studio — Backend",
    description="Turn any topic or code snippet into an animated, avatar-narrated video lesson.",
    version="0.1.0",
)

# Allow all origins for the hackathon (Lovable frontend + local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(generate.router)
app.include_router(videos.router)
