"""
MVP Pipeline — AI Video Generator
Steps:
  1. Generate TTS audio (OpenAI)
  2. Upload audio to fal.ai storage
  3. fal.ai Fabric 1.0: avatar image + audio → avatar.mp4
  4. Manim: render animation.mp4
  5. moviepy: merge animation + avatar (pip) → final.mp4
"""

import argparse
import os
import subprocess
import urllib.request
from pathlib import Path

import fal_client
from openai import OpenAI
from moviepy import VideoFileClip, CompositeVideoClip
import moviepy.video.fx

# --- Config ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
FAL_KEY = os.environ.get("FAL_KEY")

AVATAR_IMAGE_URL = (
    "https://v3.fal.media/files/koala/NLVPfOI4XL1cWT2PmmqT3_Hope.png"  # default; override via env
)
AVATAR_IMAGE_URL = os.environ.get("AVATAR_IMAGE_URL", AVATAR_IMAGE_URL)

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

DEFAULT_NARRATION = """
Welcome! Today we're exploring Dijkstra's algorithm — one of the most elegant solutions in computer science.

Dijkstra solves a simple question: what is the shortest path between two nodes in a weighted graph?

We start at node A with a distance of zero. All other nodes begin at infinity.

At each step, we visit the unvisited node with the smallest known distance.
From node A, we can reach B at cost 4, and C at cost 2. C is closer, so we visit it first.

From C, we find a shorter path to B: 2 plus 1 equals 3. Better than 4, so we update.

We continue until all reachable nodes are visited.

The result: the shortest path from A to F costs 10, following A → C → B → D → F.

That's Dijkstra — greedy, correct, and fast.
"""


def generate_tts(text: str, out_path: Path) -> Path:
    if not OPENAI_API_KEY:
        raise ValueError("Missing OPENAI_API_KEY environment variable")
    print("[1/5] Generating TTS audio...")
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )
    response.write_to_file(out_path)
    print(f"      Saved: {out_path}")
    return out_path


def upload_to_fal(file_path: Path) -> str:
    if not FAL_KEY:
        raise ValueError("Missing FAL_KEY environment variable")
    print("[2/5] Uploading audio to fal.ai...")
    url = fal_client.upload_file(file_path)
    print(f"      URL: {url}")
    return url


def generate_avatar_video(audio_url: str, out_path: Path) -> Path:
    if not FAL_KEY:
        raise ValueError("Missing FAL_KEY environment variable")
    print("[3/5] Generating avatar video via Fabric 1.0...")

    def on_queue_update(update):
        if hasattr(update, "logs"):
            for log in update.logs:
                print(f"      [fal] {log['message']}")

    result = fal_client.subscribe(
        "veed/fabric-1.0",
        arguments={
            "image_url": AVATAR_IMAGE_URL,
            "audio_url": audio_url,
            "resolution": "480p",
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    video_url = result["video"]["url"]
    print(f"      Avatar video URL: {video_url}")

    urllib.request.urlretrieve(video_url, out_path)
    print(f"      Saved: {out_path}")
    return out_path


def render_manim(script_path: Path, scene_name: str, out_dir: Path) -> Path:
    print(f"[4/5] Rendering Manim animation: {script_path} -> {scene_name}")
    if not script_path.exists():
        raise FileNotFoundError(f"Manim script not found: {script_path}")
    
    cmd = [
        "manim",
        "-ql",           # low quality for fast render; change to -qh for high
        "--output_file", "animation",
        "--media_dir", str(out_dir / "manim_media"),
        str(script_path),
        scene_name,
    ]
    subprocess.run(cmd, check=True)

    # Manim outputs to media/videos/<script>/<quality>/animation.mp4
    # With community edition, the structure is usually:
    # {media_dir}/videos/{script_name}/{quality}/animation.mp4
    script_stem = script_path.stem
    matches = list((out_dir / "manim_media").rglob(f"videos/{script_stem}/*/animation.mp4"))
    
    if not matches:
        # Fallback to broader search if specific path fails
        matches = list((out_dir / "manim_media").rglob("animation.mp4"))
        
    if not matches:
        raise FileNotFoundError("Manim output not found.")
    
    # Take the latest one if multiple matches (though there should be only one)
    target = max(matches, key=os.path.getmtime)
    print(f"      Found: {target}")
    return target


def merge_videos(animation_path: Path, avatar_path: Path, out_path: Path) -> Path:
    print("[5/5] Merging videos with moviepy...")

    with VideoFileClip(str(animation_path)) as animation, VideoFileClip(str(avatar_path)) as avatar:
        # Scale avatar to ~25% of animation width, place bottom-right
        avatar_w = int(animation.w * 0.25)
        avatar_resized = avatar.resized(width=avatar_w)

        margin = 20
        avatar_positioned = avatar_resized.with_position(
            (animation.w - avatar_resized.w - margin, animation.h - avatar_resized.h - margin)
        )

        # Loop avatar if shorter than animation, trim if longer
        if avatar_resized.duration < animation.duration:
            avatar_positioned = avatar_positioned.with_effects([moviepy.video.fx.Loop(duration=animation.duration)])
        else:
            avatar_positioned = avatar_positioned.subclipped(0, animation.duration)

        composite = CompositeVideoClip([animation, avatar_positioned])
        composite.write_videofile(str(out_path), codec="libx264", audio_codec="aac")

    print(f"      Final video: {out_path}")
    return out_path


def run(narration: str, script_path: Path, scene_name: str, output: str):
    audio_path = OUTPUT_DIR / "narration.mp3"
    avatar_path = OUTPUT_DIR / "avatar.mp4"
    final_path = Path(output)

    generate_tts(narration, audio_path)
    audio_url = upload_to_fal(audio_path)
    generate_avatar_video(audio_url, avatar_path)
    animation_path = render_manim(script_path, scene_name, OUTPUT_DIR)
    merge_videos(animation_path, avatar_path, final_path)

    print(f"\nDone! Output: {final_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Video Generator CLI")
    parser.add_argument("--narration", type=str, default=DEFAULT_NARRATION, help="The narration text for the TTS.")
    parser.add_argument("--script", type=str, default="code/explain_dijkstra.py", help="Path to the Manim script.")
    parser.add_argument("--scene", type=str, default="DijkstraScene", help="The name of the Manim Scene class.")
    parser.add_argument("--output", type=str, default="output/final.mp4", help="Path to save the final video.")

    args = parser.parse_args()
    
    run(args.narration, Path(args.script), args.scene, args.output)
