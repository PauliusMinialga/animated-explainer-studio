"""
Renders a final.mp4 for prompt-mode jobs.

Structure (same as concept/algo pipeline):
  intro.mp4  →  dark screen + info.mp3  →  outro.mp4  →  final.mp4
"""

import logging
import subprocess
from pathlib import Path

from pipeline.final_merge import merge_final

logger = logging.getLogger(__name__)


def _run(*args: str) -> None:
    subprocess.run(list(args), check=True, capture_output=True,
                   close_fds=True, stdin=subprocess.DEVNULL)


def _make_dark_info_video(info_audio: Path, out_mp4: Path) -> Path:
    """Create a 854x480 dark background video with info.mp3 as audio."""
    _run(
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=#0f172a:size=854x480:rate=24",
        "-i", str(info_audio),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(out_mp4),
    )
    return out_mp4


def render_prompt_video(job_dir: Path) -> Path:
    """
    Merges intro.mp4 + (dark bg + info.mp3) + outro.mp4 → final.mp4
    Same structure as concept/algo pipeline.
    """
    intro  = job_dir / "intro.mp4"
    outro  = job_dir / "outro.mp4"
    info   = job_dir / "info.mp3"
    out    = job_dir / "final.mp4"
    dark   = job_dir / "info_dark.mp4"

    if not intro.exists() or not outro.exists() or not info.exists():
        raise FileNotFoundError(f"Missing intro/outro/info in {job_dir}")

    logger.info("Creating dark info video from info.mp3…")
    _make_dark_info_video(info, dark)

    logger.info("Merging intro + info + outro → final.mp4…")
    merge_final(
        intro_path=intro,
        animation_path=dark,
        info_audio_path=info,
        outro_path=outro,
        out_path=out,
    )

    logger.info("Done → %s", out)
    return out
