"""fal.ai Kokoro TTS — converts narration text to audio, returns fal.media URL."""

import os
import fal_client
from config import settings


async def generate_tts(text: str) -> str:
    """Returns the fal.media URL of the generated audio (mp3)."""
    if not settings.fal_key:
        raise RuntimeError("FAL_KEY is not set")
    os.environ["FAL_KEY"] = settings.fal_key

    result = fal_client.subscribe(
        "fal-ai/kokoro",
        arguments={
            "prompt": text,
            "voice": "af_nova",
            "speed": 0.95,
        },
    )
    return result["audio"]["url"]
