"""
Generate endpoint with async job tracking.

POST /generate   → starts background pipeline, returns job_id immediately
GET  /jobs/{id}  → poll for status, progress, animation_url, tts_script

Pipeline: prompt → Mistral (manim script + 3-part narration) → Manim render → done.
TTS and avatar are handled separately by Bote's pipeline.
"""

import shutil
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from models import GenerateRequest, JobResponse, JobStatus, TTSScriptResponse
from pipeline.enrich import enrich_prompt
from pipeline.scripts import generate_scripts
from pipeline.manim_render import render_manim
from database import job_dir

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

        _set(job_id, progress="Generating scripts…")
        scripts = generate_scripts(
            enriched_prompt,
            mode=req.mode,
            level=req.level,
            mood=req.mood,
        )
        tts_script = scripts["tts_script"]

        _set(job_id, progress="Rendering animation…")
        animation_path = await render_manim(
            out_dir,
            script_str=scripts["manim_script"],
            scene_class="GeneratedScene",
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

