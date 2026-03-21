"""OpenAI TTS — generate narration audio from text."""

from pathlib import Path
from openai import AsyncOpenAI
from config import settings


async def generate_tts(text: str, out_path: Path) -> Path:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )
    response.write_to_file(out_path)
    return out_path
