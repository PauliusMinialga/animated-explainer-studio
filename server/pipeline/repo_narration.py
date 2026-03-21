"""
Stage 3: Narration assembly from Storyboard.

Collects per-scene narration from the storyboard and produces:
- A RepoNarration object (scene-level granularity)
- A TTSScript (intro/info/outro for the VEED avatar pipeline)
"""

import logging

from .repo_models import Storyboard, RepoNarration, SceneNarration

logger = logging.getLogger(__name__)


def assemble_narration(storyboard: Storyboard, repo_summary: str = "") -> RepoNarration:
    """
    Build narration from storyboard scenes.

    - intro: first scene's narration (or a summary)
    - scenes: each scene's narration
    - outro: last scene's narration (or a summary)
    """
    if not storyboard.scenes:
        return RepoNarration(
            intro=repo_summary or "Let's explore this repository.",
            scenes=[],
            outro="That's the overview of the project.",
        )

    first = storyboard.scenes[0]
    last = storyboard.scenes[-1]

    # Intro: derived from first scene
    intro = first.narration if first.narration else repo_summary or "Let's explore this project."

    # Per-scene narrations
    scene_narrations = [
        SceneNarration(scene_id=s.id, narration=s.narration)
        for s in storyboard.scenes
    ]

    # Outro: derived from last scene
    outro = last.narration if last.narration else "That covers the main architecture."

    narration = RepoNarration(
        intro=intro,
        scenes=scene_narrations,
        outro=outro,
    )

    logger.info("[repo-narration] Assembled narration: %d scenes", len(scene_narrations))
    return narration


def narration_to_tts_info(narration: RepoNarration) -> str:
    """
    Flatten scene narrations into a single 'info' string for the VEED TTS pipeline.
    Skips the first and last scenes (those become intro/outro).
    """
    middle_scenes = narration.scenes[1:-1] if len(narration.scenes) > 2 else narration.scenes
    return " ".join(s.narration for s in middle_scenes if s.narration)
