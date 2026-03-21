from enum import Enum
from typing import Any, Optional
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


class JobType(str, Enum):
    repo = "repo"
    code = "code"


class GenerateRequest(BaseModel):
    prompt: str
    url: Optional[str] = None
    mode: Mode = Mode.concept
    level: Level = Level.beginner
    mood: Mood = Mood.friendly


class TTSScriptResponse(BaseModel):
    """3-part narration for Bote's TTS pipeline."""
    intro: str
    info: str
    outro: str


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: Optional[str] = None
    job_type: Optional[JobType] = None
    # Code path (Manim)
    animation_url: Optional[str] = None
    final_url: Optional[str] = None
    # Repo path (React Flow)
    architecture: Optional[dict[str, Any]] = None
    storyboard: Optional[dict[str, Any]] = None
    narration: Optional[dict[str, Any]] = None
    # Shared
    tts_script: Optional[TTSScriptResponse] = None
    error: Optional[str] = None
