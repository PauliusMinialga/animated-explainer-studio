"""
Bote's VEED pipeline — clean async wrapper for the server.

Given a TTSScript and job output dir:
  1. Runware TTS → intro.mp3, info.mp3, outro.mp3
  2. fal.ai (VEED Fabric 1.0) → intro.mp4, outro.mp4 (talking-head avatar)

Returns paths to the 4 output files.
"""

import asyncio
import base64
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests as _requests
import fal_client
from runware import Runware, IAudioInference, IAudioSpeech

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class VeedResult:
    intro_video: Path
    info_audio: Path
    outro_video: Path


async def _tts(text: str, out_path: Path, voice: str = "Oliver") -> Path:
    """Runware TTS → mp3 file."""
    runware = Runware(api_key=settings.runware_api_key)
    await runware.connect()
    try:
        results = await runware.audioInference(
            requestAudio=IAudioInference(
                model="inworld:tts@1.5-mini",
                speech=IAudioSpeech(text=text, voice=voice),
            )
        )
        audio = results[0]
        if audio.audioURL:
            resp = _requests.get(audio.audioURL)
            out_path.write_bytes(resp.content)
        elif audio.audioBase64Data:
            out_path.write_bytes(base64.b64decode(audio.audioBase64Data))
        else:
            raise RuntimeError("Runware returned no audio data")
    finally:
        await runware.disconnect()
    return out_path


async def generate_tts_audio(text: str, out_path: Path, voice: str = "Oliver") -> Path:
    """Public wrapper for TTS generation — used by repo pipeline for per-scene audio."""
    if not settings.runware_api_key:
        raise RuntimeError("RUNWARE_API_KEY is not set")
    return await _tts(text, out_path, voice=voice)


async def _avatar_video(audio_path: Path, out_path: Path, image_url: Optional[str] = None) -> Path:
    """fal.ai VEED Fabric 1.0: audio + avatar image → mp4 URL → downloaded file."""
    os.environ["FAL_KEY"] = settings.fal_key

    audio_url = fal_client.upload_file(str(audio_path))
    image_url = image_url or settings.avatar_image_url

    result = fal_client.run(
        "veed/fabric-1.0",
        arguments={
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": "480p",
        },
    )
    video_url = result["video"]["url"]
    resp = _requests.get(video_url)
    out_path.write_bytes(resp.content)
    return out_path


async def run_veed_pipeline(
    intro_text: str,
    info_text: str,
    outro_text: str,
    job_dir: Path,
    avatar_image_url: Optional[str] = None,
    voice: str = "Oliver",
) -> VeedResult:
    """
    Full Bote pipeline for one job.
    Generates 3 TTS audio files and 2 avatar videos (intro + outro).
    """
    if not settings.runware_api_key:
        raise RuntimeError("RUNWARE_API_KEY is not set")
    if not settings.fal_key:
        raise RuntimeError("FAL_KEY is not set")

    intro_mp3 = job_dir / "intro.mp3"
    info_mp3 = job_dir / "info.mp3"
    outro_mp3 = job_dir / "outro.mp3"

    logger.info("Generating TTS audio (intro + info + outro) voice=%s…", voice)
    await asyncio.gather(
        _tts(intro_text, intro_mp3, voice=voice),
        _tts(info_text, info_mp3, voice=voice),
        _tts(outro_text, outro_mp3, voice=voice),
    )

    logger.info("Generating avatar videos (intro + outro) — image: %s", avatar_image_url or "default")
    intro_mp4 = job_dir / "intro.mp4"
    outro_mp4 = job_dir / "outro.mp4"
    await asyncio.gather(
        _avatar_video(intro_mp3, intro_mp4, image_url=avatar_image_url),
        _avatar_video(outro_mp3, outro_mp4, image_url=avatar_image_url),
    )

    return VeedResult(
        intro_video=intro_mp4,
        info_audio=info_mp3,
        outro_video=outro_mp4,
    )
