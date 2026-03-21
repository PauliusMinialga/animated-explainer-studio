"""
Generate endpoint with async job tracking.

POST /generate   → starts background pipeline, returns job_id immediately
GET  /jobs/{id}  → poll for status, progress, results

Pipeline:
  - If prompt is a github.com URL → repo analysis → storyboard → narration (React Flow)
  - Otherwise → generate_scripts → Manim render → VEED → final merge (video)
"""

import asyncio
import json
import logging
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from models import GenerateRequest, JobResponse, JobStatus, JobType, TTSScriptResponse
from pipeline.enrich import enrich_prompt, ingest_github_repo
from pipeline.scripts import generate_scripts
from pipeline.manim_render import render_manim
from pipeline.veed_pipeline import run_veed_pipeline, generate_tts_audio
from pipeline.final_merge import merge_final
from pipeline.repo_analysis import analyze_repo
from pipeline.repo_storyboard import generate_storyboard
from pipeline.repo_narration import assemble_narration, narration_to_tts_info
from database import job_dir
from config import settings
from supabase_client import update_request_status

logger = logging.getLogger(__name__)

router = APIRouter(tags=["generate"])

_jobs: dict[str, dict] = {}


def _set(job_id: str, **kwargs):
    _jobs[job_id].update(kwargs)


@router.post("/generate", response_model=JobResponse, status_code=202)
async def generate(req: GenerateRequest, background_tasks: BackgroundTasks, request: Request):
    job_id = str(uuid.uuid4())
    base_url = str(request.base_url).rstrip("/")
    _jobs[job_id] = {
        "status": JobStatus.pending,
        "progress": "Queued",
        "job_type": None,
        "animation_url": None,
        "final_url": None,
        "architecture": None,
        "storyboard": None,
        "narration": None,
        "tts_script": None,
        "error": None,
    }
    background_tasks.add_task(_run_pipeline, job_id, req, base_url)
    return JobResponse(job_id=job_id, status=JobStatus.pending, progress="Queued")


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(job_id=job_id, **job)


async def _run_pipeline(job_id: str, req: GenerateRequest, base_url: str = "http://localhost:8000"):
    rid = req.request_id  # Supabase video_requests row ID (may be None)
    try:
        out_dir = job_dir(job_id)
        is_github_url = req.prompt.strip().startswith("https://github.com/")

        if rid:
            update_request_status(rid, "processing")

        if is_github_url:
            await _run_repo_pipeline(job_id, req, out_dir, base_url)
        else:
            await _run_code_pipeline(job_id, req, out_dir, base_url)

        if rid:
            video_url = _jobs[job_id].get("final_url")
            update_request_status(rid, "completed", video_url=video_url)

    except HTTPException as exc:
        _set(job_id, status=JobStatus.failed, progress="Failed", error=exc.detail)
        if rid:
            update_request_status(rid, "failed", error=exc.detail)
        raise
    except Exception as exc:
        _set(job_id, status=JobStatus.failed, progress="Failed", error=str(exc))
        if rid:
            update_request_status(rid, "failed", error=str(exc))
        raise


# ── Repo pipeline (React Flow) ───────────────────────────────────────────────

async def _run_repo_pipeline(
    job_id: str, req: GenerateRequest, out_dir: Path, base_url: str,
):
    _set(job_id, status=JobStatus.running, job_type=JobType.repo, progress="Ingesting GitHub repo…")
    logger.info("[%s] Ingesting repo: %s", job_id, req.prompt.strip())

    try:
        repo_content = await ingest_github_repo(req.prompt.strip())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Could not fetch repo (HTTP {exc.response.status_code}): {req.prompt}",
        )
    logger.info("[%s] Repo ingested — %d chars", job_id, len(repo_content))

    # Stage 1: Architecture
    _set(job_id, progress="Analyzing architecture…")
    architecture = await asyncio.to_thread(
        analyze_repo, repo_content, req.mood, req.level,
    )
    arch_dict = architecture.model_dump(by_alias=True)
    (out_dir / "architecture.json").write_text(json.dumps(arch_dict, indent=2))
    _set(job_id, architecture=arch_dict)

    # Stage 2: Storyboard
    _set(job_id, progress="Generating storyboard…")
    storyboard = await asyncio.to_thread(generate_storyboard, architecture)
    sb_dict = storyboard.model_dump()
    (out_dir / "storyboard.json").write_text(json.dumps(sb_dict, indent=2))
    _set(job_id, storyboard=sb_dict)

    # Stage 3: Narration (assembly + LLM polish pass)
    _set(job_id, progress="Polishing narration…")
    narration = await asyncio.to_thread(assemble_narration, storyboard, architecture.summary)
    narr_dict = narration.model_dump()

    # ── Per-scene TTS audio ───────────────────────────────────────────────────
    if settings.runware_api_key:
        _set(job_id, progress="Generating scene audio…")
        logger.info("[%s] Generating per-scene TTS (%d scenes)", job_id, len(narration.scenes))

        # Generate all scene audio files in parallel
        scene_tts_tasks = []
        for i, sn in enumerate(narration.scenes):
            if sn.narration.strip():
                out_path = out_dir / f"scene_{i}.mp3"
                scene_tts_tasks.append((i, generate_tts_audio(sn.narration, out_path)))

        for i, task in scene_tts_tasks:
            try:
                await task
                narr_dict["scenes"][i]["audio_url"] = f"{base_url}/files/{job_id}/scene_{i}.mp3"
                logger.info("[%s] Scene %d TTS done", job_id, i)
            except Exception as exc:
                logger.warning("[%s] Scene %d TTS failed: %s", job_id, i, exc)

    (out_dir / "narration.json").write_text(json.dumps(narr_dict, indent=2))
    _set(job_id, narration=narr_dict)

    # Build TTS script for VEED avatars (intro/outro)
    tts_info = narration_to_tts_info(narration)
    tts_response = TTSScriptResponse(
        intro=narration.intro,
        info=tts_info,
        outro=narration.outro,
    )
    _set(job_id, tts_script=tts_response)

    logger.info(
        "[%s] ── TTS SCRIPT ───\n  INTRO: %s\n  INFO:  %s\n  OUTRO: %s\n───────",
        job_id, narration.intro, tts_info[:200], narration.outro,
    )

    # ── Avatar videos (intro + outro talking head) ────────────────────────────
    if settings.runware_api_key and settings.fal_key:
        _set(job_id, progress="Generating avatar videos…")
        try:
            veed = await asyncio.wait_for(
                run_veed_pipeline(
                    intro_text=narration.intro,
                    info_text=tts_info,
                    outro_text=narration.outro,
                    job_dir=out_dir,
                ),
                timeout=300,  # 5 min hard cap — avatar gen can hang
            )
            # Inject video URLs into narration dict
            narr_dict["intro_video_url"] = f"{base_url}/files/{job_id}/intro.mp4"
            narr_dict["outro_video_url"] = f"{base_url}/files/{job_id}/outro.mp4"
            _set(job_id, narration=narr_dict)
        except asyncio.TimeoutError:
            logger.warning("[%s] VEED avatar pipeline timed out after 300s (non-fatal)", job_id)
        except Exception as exc:
            logger.warning("[%s] VEED avatar pipeline failed (non-fatal): %s", job_id, exc)

    _set(job_id, status=JobStatus.done, progress="Done")


# ── Code pipeline (Manim) ────────────────────────────────────────────────────

async def _run_code_pipeline(
    job_id: str, req: GenerateRequest, out_dir: Path, base_url: str,
):
    _set(job_id, status=JobStatus.running, job_type=JobType.code, progress="Enriching prompt…")
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

    logger.info(
        "[%s] ── TTS SCRIPT ───\n  INTRO: %s\n  INFO:  %s\n  OUTRO: %s\n───────",
        job_id, tts.intro, tts.info, tts.outro,
    )

    (out_dir / "tts_script.json").write_text(
        json.dumps({"intro": tts.intro, "info": tts.info, "outro": tts.outro}, indent=2),
    )
    (out_dir / "manim_script.py").write_text(manim_script)

    # Render Manim
    _set(job_id, progress="Rendering animation…")
    animation_path = await render_manim(
        out_dir, script_str=manim_script, scene_class="GeneratedScene",
    )
    final_animation = out_dir / "animation.mp4"
    shutil.copy2(animation_path, final_animation)

    tts_response = TTSScriptResponse(intro=tts.intro, info=tts.info, outro=tts.outro)
    _set(
        job_id,
        progress="Generating avatar & voice…",
        animation_url=f"{base_url}/files/{job_id}/animation.mp4",
        tts_script=tts_response,
    )

    # VEED pipeline
    if settings.runware_api_key and settings.fal_key:
        veed = await run_veed_pipeline(
            intro_text=tts.intro,
            info_text=tts.info,
            outro_text=tts.outro,
            job_dir=out_dir,
        )

        _set(job_id, progress="Assembling final video…")
        final_path = out_dir / "final.mp4"
        await asyncio.to_thread(
            merge_final,
            intro_path=veed.intro_video,
            animation_path=final_animation,
            info_audio_path=veed.info_audio,
            outro_path=veed.outro_video,
            out_path=final_path,
        )
        _set(job_id, final_url=f"{base_url}/files/{job_id}/final.mp4")

    _set(job_id, status=JobStatus.done, progress="Done")

