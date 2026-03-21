"""
Generate endpoint with async job tracking.

POST /generate   → starts background pipeline, returns job_id immediately
GET  /jobs/{id}  → poll for status, progress, animation_url, tts_script

Pipeline:
  - If prompt is a github.com URL → ingest repo via gitingest.com → generate_repo_scripts
  - Otherwise → generate_scripts (concept / code mode)
  Both paths: Manim render → write files → return job.

TTS and avatar are handled separately by Bote's pipeline.
"""

import json
import logging
import shutil
import uuid

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException

from models import GenerateRequest, JobResponse, JobStatus, TTSScriptResponse
from pipeline.enrich import enrich_prompt, ingest_github_repo
from pipeline.scripts import generate_scripts, generate_repo_scripts
from pipeline.manim_render import render_manim
from database import job_dir

logger = logging.getLogger(__name__)

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
        is_github_url = req.prompt.strip().startswith("https://github.com/")

        if is_github_url:
            _set(job_id, status=JobStatus.running, progress="Ingesting GitHub repo…")
            logger.info("[%s] Ingesting repo: %s", job_id, req.prompt.strip())
            try:
                repo_content = await ingest_github_repo(req.prompt.strip())
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc))
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                raise HTTPException(
                    status_code=status,
                    detail=f"Could not fetch repo (HTTP {status}): {req.prompt}",
                )
            logger.info("[%s] Repo ingested — %d chars", job_id, len(repo_content))

            _set(job_id, progress="Generating repo scripts…")
            manim_script, tts = generate_repo_scripts(
                url=req.prompt.strip(),
                repo_content=repo_content,
                mood=req.mood,
                level=req.level,
            )
        else:
            _set(job_id, status=JobStatus.running, progress="Enriching prompt…")
            enriched_prompt = await enrich_prompt(req.prompt, req.url)

            _set(job_id, progress="Generating scripts…")
            scripts = generate_scripts(
                enriched_prompt,
                mode=req.mode,
                level=req.level,
                mood=req.mood,
            )
            manim_script = scripts["manim_script"]
            tts = scripts["tts_script"]

        # ── Debug: print generated artefacts to console ──────────────────────
        logger.info(
            "[%s] ── MANIM SCRIPT ──────────────────────────────────\n%s\n"
            "─────────────────────────────────────────────────────",
            job_id, manim_script,
        )
        logger.info(
            "[%s] ── TTS SCRIPT ───────────────────────────────────\n"
            "  INTRO: %s\n  INFO:  %s\n  OUTRO: %s\n"
            "─────────────────────────────────────────────────────",
            job_id, tts.intro, tts.info, tts.outro,
        )

        # Persist raw Manim script for debugging
        (out_dir / "manim_script.py").write_text(manim_script, encoding="utf-8")

        _set(job_id, progress="Rendering animation…")
        animation_path = await render_manim(
            out_dir,
            script_str=manim_script,
            scene_class="GeneratedScene",
        )

        final_animation = out_dir / "animation.mp4"
        if animation_path != final_animation:
            shutil.copy2(animation_path, final_animation)

        tts_response = TTSScriptResponse(
            intro=tts.intro,
            info=tts.info,
            outro=tts.outro,
        )

        # Persist TTS script as JSON for Bote's pipeline
        (out_dir / "tts_script.json").write_text(
            json.dumps({"intro": tts.intro, "info": tts.info, "outro": tts.outro}, indent=2),
            encoding="utf-8",
        )

        _set(
            job_id,
            status=JobStatus.done,
            progress="Done",
            animation_url=f"/files/{job_id}/animation.mp4",
            tts_script=tts_response,
        )

    except HTTPException as exc:
        _set(job_id, status=JobStatus.failed, progress="Failed", error=exc.detail)
        raise
    except Exception as exc:
        _set(job_id, status=JobStatus.failed, progress="Failed", error=str(exc))
        raise

