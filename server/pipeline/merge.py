"""moviepy video merge — overlay avatar in bottom-right corner of animation."""

from pathlib import Path
from moviepy import VideoFileClip, CompositeVideoClip
import moviepy.video.fx


def merge_videos(
    animation_path: Path,
    avatar_path: Path,
    out_path: Path,
) -> Path:
    with (
        VideoFileClip(str(animation_path)) as animation,
        VideoFileClip(str(avatar_path)) as avatar,
    ):
        avatar_w = int(animation.w * 0.25)
        avatar_resized = avatar.resized(width=avatar_w)

        margin = 20
        avatar_positioned = avatar_resized.with_position(
            (
                animation.w - avatar_resized.w - margin,
                animation.h - avatar_resized.h - margin,
            )
        )

        if avatar_resized.duration < animation.duration:
            avatar_positioned = avatar_positioned.with_effects(
                [moviepy.video.fx.Loop(duration=animation.duration)]
            )
        else:
            avatar_positioned = avatar_positioned.subclipped(0, animation.duration)

        composite = CompositeVideoClip([animation, avatar_positioned])
        composite.write_videofile(str(out_path), codec="libx264", audio_codec="aac")

    return out_path
