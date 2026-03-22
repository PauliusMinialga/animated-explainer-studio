"""
Renders a final.mp4 for prompt-mode jobs.

Structure:
  intro.mp4  →  scene_0 card + audio  →  …  →  scene_N card + audio  →  outro.mp4
                                    → final.mp4

Each scene card is:
  - 854×480, dark (#0F172A) background
  - Scene title (white, large)
  - Up to 3 bullet points (gray)
  - Duration = length of scene audio
"""

import json
import logging
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

W, H = 854, 480
BG_COLOR = (15, 23, 42)       # #0F172A
TITLE_COLOR = (255, 255, 255)
BULLET_COLOR = (148, 163, 184) # slate-400
ACCENT_COLOR = (96, 165, 250)  # blue-400

FONT_REGULAR = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_BOLD    = "/System/Library/Fonts/HelveticaNeue.ttc"

SCALE_FILTER = "scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2,setsar=1"


def _load_font(path: str, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        idx = 1 if bold else 0
        return ImageFont.truetype(path, size, index=idx)
    except Exception:
        return ImageFont.load_default()


def _audio_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_streams", str(path)],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        for s in data.get("streams", []):
            if "duration" in s:
                return float(s["duration"])
    except Exception:
        pass
    return 5.0


def _run(cmd: list[str]) -> None:
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        stdin=subprocess.DEVNULL, close_fds=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-1000:]}")


def _make_scene_image(title: str, bullets: list[str], out_png: Path) -> None:
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_title  = _load_font(FONT_BOLD,    36, bold=True)
    font_bullet = _load_font(FONT_REGULAR, 22)
    font_num    = _load_font(FONT_REGULAR, 18)

    # Accent bar top
    draw.rectangle([(0, 0), (W, 4)], fill=ACCENT_COLOR)

    # Title — wrapped to ~55 chars
    wrapped = textwrap.wrap(title, width=50)
    y = 80
    for line in wrapped[:2]:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y), line, font=font_title, fill=TITLE_COLOR)
        y += 48

    # Divider
    y += 16
    draw.rectangle([(W // 2 - 120, y), (W // 2 + 120, y + 2)], fill=ACCENT_COLOR)
    y += 24

    # Bullets (up to 3)
    for i, bullet in enumerate(bullets[:3]):
        wrapped_b = textwrap.wrap(bullet, width=60)
        line_text = (wrapped_b[0] + "…") if len(wrapped_b) > 1 else (wrapped_b[0] if wrapped_b else bullet)
        # bullet dot
        draw.ellipse([(W // 2 - 200, y + 8), (W // 2 - 192, y + 16)], fill=ACCENT_COLOR)
        draw.text((W // 2 - 184, y), line_text, font=font_bullet, fill=BULLET_COLOR)
        y += 40

    img.save(str(out_png))


def _make_scene_video(png: Path, audio: Path, out_mp4: Path) -> None:
    duration = _audio_duration(audio)
    _run([
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(duration + 0.5), "-i", str(png),
        "-i", str(audio),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-vf", f"scale={W}:{H},setsar=1",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(out_mp4),
    ])


def _scale_avatar(src: Path, out: Path) -> None:
    """Scale portrait avatar video to 854×480 with pillarbox."""
    _run([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", SCALE_FILTER,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        str(out),
    ])


def render_prompt_video(job_dir: Path) -> Path:
    """
    Reads storyboard.json + narration.json from job_dir,
    renders title cards for each scene, and concatenates:
        intro → scene cards → outro → final.mp4
    Returns the path to final.mp4.
    """
    out_final = job_dir / "final.mp4"

    storyboard_path = job_dir / "storyboard.json"
    narration_path  = job_dir / "narration.json"

    storyboard = json.loads(storyboard_path.read_text())
    narration  = json.loads(narration_path.read_text())

    scenes     = storyboard.get("scenes", [])
    nar_scenes = narration.get("scenes", [])

    # Build lookup: scene_id → narration info
    nar_by_id = {s["scene_id"]: s for s in nar_scenes}

    # --- Scale intro / outro ---
    intro_scaled = job_dir / "intro_scaled.mp4"
    outro_scaled = job_dir / "outro_scaled.mp4"

    logger.info("Scaling intro/outro avatar videos…")
    _scale_avatar(job_dir / "intro.mp4", intro_scaled)
    _scale_avatar(job_dir / "outro.mp4", outro_scaled)

    # --- Render scene cards ---
    scene_videos: list[Path] = []
    for i, scene in enumerate(scenes):
        scene_id = scene.get("id", f"scene_{i+1}")
        title    = scene.get("title", f"Scene {i+1}")
        bullets  = [b for b in scene.get("panel", {}).get("bullets", [])]

        audio_file = job_dir / f"scene_{i}.mp3"
        if not audio_file.exists():
            logger.warning("Missing %s — skipping scene", audio_file.name)
            continue

        png = job_dir / f"scene_{i}_card.png"
        mp4 = job_dir / f"scene_{i}_card.mp4"

        logger.info("Rendering scene card %d/%d: %s", i + 1, len(scenes), title)
        _make_scene_image(title, bullets, png)
        _make_scene_video(png, audio_file, mp4)
        scene_videos.append(mp4)

    # --- Concatenate ---
    segments = [intro_scaled] + scene_videos + [outro_scaled]

    concat_list = job_dir / "concat.txt"
    with open(concat_list, "w") as f:
        for seg in segments:
            f.write(f"file '{seg.resolve()}'\n")

    logger.info("Concatenating %d segments → final.mp4", len(segments))
    _run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        str(out_final),
    ])

    logger.info("Done → %s", out_final)
    return out_final
