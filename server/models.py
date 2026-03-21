from enum import Enum
from typing import Optional
from pydantic import BaseModel


class Mode(str, Enum):
    concept = "concept"
    code = "code"


class Level(str, Enum):
    beginner = "beginner"
    advanced = "advanced"
    expert = "expert"


class Mood(str, Enum):
    friendly = "friendly"
    technical = "technical"
    energetic = "energetic"
    calm = "calm"


class GenerateRequest(BaseModel):
    prompt: str
    url: Optional[str] = None
    mode: Mode = Mode.concept
    level: Level = Level.beginner
    mood: Mood = Mood.friendly
    avatar_image_url: Optional[str] = None


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: Optional[str] = None
    animation_url: Optional[str] = None   # Manim output
    avatar_url: Optional[str] = None      # fal.ai talking-head output
    error: Optional[str] = None


class CachedVideo(BaseModel):
    slug: str
    title: str
    description: str
    category: str
    tags: list[str]
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    # Whether a pre-built Manim script exists locally
    has_script: bool = False
