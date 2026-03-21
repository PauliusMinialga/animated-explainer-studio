"""fal.ai avatar video generation (VEED Fabric 1.0)."""

import urllib.request
from pathlib import Path
import fal_client
from config import settings


async def upload_audio(audio_path: Path) -> str:
    """Upload audio file to fal.ai storage and return URL."""
    if not settings.fal_key:
        raise RuntimeError("FAL_KEY is not set")
    import os
    os.environ["FAL_KEY"] = settings.fal_key
    return fal_client.upload_file(str(audio_path))


async def generate_avatar(
    audio_url: str,
    out_path: Path,
    avatar_image_url: str | None = None,
) -> Path:
    """Generate a talking-head avatar video and save to out_path."""
    if not settings.fal_key:
        raise RuntimeError("FAL_KEY is not set")

    import os
    os.environ["FAL_KEY"] = settings.fal_key

    image_url = avatar_image_url or settings.avatar_image_url

    def on_queue_update(update):
        if hasattr(update, "logs"):
            for log in update.logs:
                print(f"[fal] {log['message']}")

    result = fal_client.subscribe(
        "veed/fabric-1.0",
        arguments={
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": "480p",
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    video_url = result["video"]["url"]
    urllib.request.urlretrieve(video_url, out_path)
    return out_path
