"""
Async Manim renderer.

Accepts either a script string (Claude-generated) or a path to an existing script.
Writes temp files as needed, runs `manim -ql`, returns the path to the output mp4.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path


async def render_manim(
    out_dir: Path,
    *,
    script_str: str | None = None,
    script_path: Path | None = None,
    scene_class: str = "GeneratedScene",
    output_name: str = "animation",
) -> Path:
    """
    Render a Manim scene and return the path to animation.mp4.

    Pass exactly one of `script_str` (raw Python code) or `script_path` (existing file).
    """
    if script_str is None and script_path is None:
        raise ValueError("Provide either script_str or script_path")

    tmp_file = None
    try:
        if script_str is not None:
            tmp_file = tempfile.NamedTemporaryFile(
                suffix=".py", delete=False, mode="w", encoding="utf-8"
            )
            tmp_file.write(script_str)
            tmp_file.close()
            target = Path(tmp_file.name)
        else:
            target = script_path  # type: ignore[assignment]

        media_dir = out_dir / "manim_media"
        media_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable, "-m", "manim",
            "-ql",
            "--output_file", output_name,
            "--media_dir", str(media_dir),
            str(target),
            scene_class,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(
                f"Manim render failed (exit {proc.returncode}):\n"
                f"{stderr.decode()[-2000:]}"
            )

        # Locate output
        stem = target.stem
        matches = list(media_dir.rglob(f"videos/{stem}/*/{output_name}.mp4"))
        if not matches:
            matches = list(media_dir.rglob(f"{output_name}.mp4"))
        if not matches:
            matches = list(media_dir.rglob("*.mp4"))
        if not matches:
            raise FileNotFoundError("Manim output not found after render")

        return max(matches, key=os.path.getmtime)

    finally:
        if tmp_file and Path(tmp_file.name).exists():
            Path(tmp_file.name).unlink(missing_ok=True)
