"""
Generate endpoint with async job tracking.

POST /generate   → starts background pipeline, returns job_id immediately
GET  /jobs/{id}  → poll for status, progress, animation_url, avatar_url

Videos are saved locally and served via GET /files/{job_id}/{filename}.
No server-side merge: both videos composited in the browser via CSS overlay.
"""

import asyncio
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

from models import GenerateRequest, JobResponse, JobStatus
from pipeline.enrich import enrich_prompt
from pipeline.scripts import generate_scripts
from pipeline.manim_render import render_manim
from pipeline.tts import generate_tts
from pipeline.avatar import generate_avatar
from database import job_dir
from catalog import CATALOG_BY_SLUG

router = APIRouter(tags=["generate"])

# In-memory job store — sufficient for hackathon
_jobs: dict[str, dict] = {}


def _set(job_id: str, **kwargs):
    _jobs[job_id].update(kwargs)


@router.post("/generate", response_model=JobResponse, status_code=202)
async def generate(req: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status": JobStatus.pending,
        "progress": "Queued",
        "animation_url": None,
        "avatar_url": None,
        "error": None,
    }
    background_tasks.add_task(_run_pipeline, job_id, req)
    return JobResponse(job_id=job_id, status=JobStatus.pending, progress="Queued")


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(job_id=job_id, **job)


async def _run_pipeline(job_id: str, req: GenerateRequest):
    try:
        out_dir = job_dir(job_id)

        _set(job_id, status=JobStatus.running, progress="Enriching prompt…")
        enriched_prompt = await enrich_prompt(req.prompt, req.url)

        # Check if prompt matches a pre-built catalog entry
        slug_guess = req.prompt.strip().lower().replace(" ", "-")
        catalog_entry = CATALOG_BY_SLUG.get(slug_guess)
        use_cached_script = catalog_entry and catalog_entry.has_script

        _set(job_id, progress="Generating scripts with Claude…")
        scripts = generate_scripts(
            enriched_prompt,
            mode=req.mode,
            level=req.level,
            mood=req.mood,
        )
        narration = scripts["narration"]

        if use_cached_script:
            script_path = Path(__file__).parent.parent / catalog_entry.script_path
            scene_class = catalog_entry.scene_class
            manim_script_str = None
        else:
            script_path = None
            scene_class = "GeneratedScene"
            manim_script_str = scripts["manim_script"]

        _set(job_id, progress="Rendering animation & generating voice in parallel…")

        async def _render():
            return await render_manim(
                out_dir,
                script_str=manim_script_str,
                script_path=script_path,
                scene_class=scene_class,
            )

        # Manim render and Kokoro TTS run in parallel
        animation_path, audio_url = await asyncio.gather(_render(), generate_tts(narration))

        _set(job_id, progress="Generating avatar video…")
        avatar_path = out_dir / "avatar.mp4"
        await generate_avatar(
            audio_url,
            avatar_path,
            avatar_image_url=req.avatar_image_url,
        )

        # Copy animation to a stable output path
        final_animation = out_dir / "animation.mp4"
        if animation_path != final_animation:
            shutil.copy2(animation_path, final_animation)

        _set(
            job_id,
            status=JobStatus.done,
            progress="Done",
            animation_url=f"/files/{job_id}/animation.mp4",
            avatar_url=f"/files/{job_id}/avatar.mp4",
        )

    except Exception as exc:
        _set(job_id, status=JobStatus.failed, progress="Failed", error=str(exc))
        raise

