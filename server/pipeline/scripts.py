"""
Claude script generation.

Given a topic/prompt, returns a Manim animation script and a narration text.
The Manim scene class is always named `GeneratedScene` so the renderer can
call it without knowing the original class name.
"""

import re
import anthropic
from config import settings

_SYSTEM_PROMPT = """You are an expert Manim animator and computer science educator.

Given a topic, experience level, and mood, return TWO things:

1. A complete, runnable Manim (Community Edition) Python script
2. A narration text to be read aloud while the animation plays

MANIM RULES (follow strictly):
- The Scene class MUST be named exactly `GeneratedScene`
- Import only: `from manim import *`
- Do NOT use MathTex or LaTeX — use Text() or Tex() with simple expressions only
- Do NOT use external images or fonts
- Target 30–60 seconds total runtime
- Use clear colours: WHITE, YELLOW, BLUE, GREEN, RED on a dark background
- Keep it educational: show one concept at a time, use labels and annotations

NARRATION RULES:
- Plain spoken English — no markdown, no bullet points
- Should match the visual timeline (explain what's appearing on screen)
- ~150 words per minute pace; aim for 75–150 words total
- End with a clear takeaway

Return your response in this EXACT format (XML tags on their own lines):

<manim_script>
[complete Python code]
</manim_script>

<narration>
[spoken narration text]
</narration>"""


def _build_user_prompt(prompt: str, mode: str, level: str, mood: str) -> str:
    return (
        f"Mode: {mode}\n"
        f"Experience level: {level}\n"
        f"Mood/tone: {mood}\n\n"
        f"Topic / Input:\n{prompt}"
    )


def _parse_response(content: str) -> dict[str, str]:
    manim_match = re.search(
        r"<manim_script>\s*(.*?)\s*</manim_script>", content, re.DOTALL
    )
    narration_match = re.search(
        r"<narration>\s*(.*?)\s*</narration>", content, re.DOTALL
    )

    if not manim_match or not narration_match:
        raise ValueError(
            "Claude response did not contain expected <manim_script> and <narration> tags.\n"
            f"Response was:\n{content[:500]}"
        )

    return {
        "manim_script": manim_match.group(1).strip(),
        "narration": narration_match.group(1).strip(),
    }


def generate_scripts(
    prompt: str,
    mode: str = "concept",
    level: str = "beginner",
    mood: str = "friendly",
) -> dict[str, str]:
    """
    Returns {"manim_script": str, "narration": str}.
    Raises on API error or malformed response.
    """
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": _build_user_prompt(prompt, mode, level, mood),
            }
        ],
    )

    raw = message.content[0].text
    return _parse_response(raw)
