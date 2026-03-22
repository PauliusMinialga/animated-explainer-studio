"""
Pipeline package for the Animated Explainer Studio backend.

Contains two main paths:
- Code/concept explanation: scripts.py → manim_render.py → veed_pipeline.py → final_merge.py
- Repo explanation: enrich.py → repo_analysis.py → repo_storyboard.py → repo_narration.py
"""

import re


def strip_json_fences(raw: str) -> str:
    """Remove markdown ```json fences from LLM output. Used by repo_analysis and repo_storyboard."""
    raw = re.sub(r"^```[a-z]*\n?", "", raw.strip())
    return re.sub(r"\n?```$", "", raw.strip())
