"""
Generate endpoint with async job tracking.

POST /generate   → starts background pipeline, returns job_id immediately
GET  /jobs/{id}  → poll for status, progress, animation_url, tts_script

Pipeline: prompt → Mistral (manim script + 3-part narration) → Manim render → done.
TTS and avatar are handled separately by Bote's pipeline.
"""

import asyncio
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

from models import GenerateRequest, JobResponse, JobStatus, TTSScriptResponse
from pipeline.enrich import enrich_prompt
from pipeline.scripts import generate_scripts
from pipeline.manim_render import render_manim
from database import job_dir
from catalog import CATALOG_BY_SLUG

router = APIRouter(tags=["generate"])

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
        "tts_script": None,
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

        _set(job_id, progress="Generating scripts…")
        scripts = generate_scripts(
            enriched_prompt,
            mode=req.mode,
            level=req.level,
            mood=req.mood,
        )
        tts_script = scripts["tts_script"]

        if use_cached_script:
            script_path = Path(__file__).parent.parent / catalog_entry.script_path
            scene_class = catalog_entry.scene_class
            manim_script_str = None
        else:
            script_path = None
            scene_class = "GeneratedScene"
            manim_script_str = scripts["manim_script"]

        _set(job_id, progress="Rendering animation…")
        animation_path = await render_manim(
            out_dir,
            script_str=manim_script_str,
            script_path=script_path,
            scene_class=scene_class,
        )

        final_animation = out_dir / "animation.mp4"
        if animation_path != final_animation:
            shutil.copy2(animation_path, final_animation)

        _set(
            job_id,
            status=JobStatus.done,
            progress="Done",
            animation_url=f"/files/{job_id}/animation.mp4",
            tts_script=TTSScriptResponse(
                intro=tts_script.intro,
                info=tts_script.info,
                outro=tts_script.outro,
            ),
        )

    except Exception as exc:
        _set(job_id, status=JobStatus.failed, progress="Failed", error=str(exc))
        raise

