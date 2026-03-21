"""
Mistral script generation.

Given a prompt, returns a Manim animation script and a narration text.
The Manim scene class is always named `GeneratedScene`.
"""

import re
from mistralai import Mistral
from config import settings

_SYSTEM_PROMPT = """You are an expert Manim animator and computer science educator.

Given a topic or code snippet, experience level, and mood, return TWO things:
1. A complete, runnable Manim (Community Edition) Python script
2. A narration text to be read aloud while the animation plays

MANIM RULES (follow strictly):
- The Scene class MUST be named exactly `GeneratedScene`
- Import only: `from manim import *`
- Do NOT use MathTex or LaTeX — use Text() for all text
- Do NOT use external images or fonts
- Target 30–60 seconds total runtime
- Use clear colours: WHITE, YELLOW, BLUE, GREEN, RED on dark background
- Show one concept at a time with labels and annotations

NARRATION RULES:
- Plain spoken English, no markdown
- Match the visual timeline (explain what's appearing on screen)
- ~150 words per minute pace; aim for 75–150 words total
- End with a clear takeaway

Return ONLY this exact format:

<manim_script>
[complete Python code]
</manim_script>

<narration>
[spoken narration text]
</narration>"""


def _build_user_prompt(prompt: str, mode: str, level: str, mood: str) -> str:
    return f"Mode: {mode}\nExperience level: {level}\nMood/tone: {mood}\n\nInput:\n{prompt}"


def _parse(content: str) -> dict[str, str]:
    manim = re.search(r"<manim_script>\s*(.*?)\s*</manim_script>", content, re.DOTALL)
    narration = re.search(r"<narration>\s*(.*?)\s*</narration>", content, re.DOTALL)
    if not manim or not narration:
        raise ValueError(
            "Response missing <manim_script> or <narration> tags.\n"
            f"Response preview:\n{content[:500]}"
        )
    return {"manim_script": manim.group(1).strip(), "narration": narration.group(1).strip()}


def generate_scripts(prompt: str, mode: str = "code", level: str = "beginner", mood: str = "friendly") -> dict[str, str]:
    """Returns {"manim_script": str, "narration": str}."""
    if not settings.mistral_api_key:
        raise RuntimeError("MISTRAL_API_KEY is not set")

    client = Mistral(api_key=settings.mistral_api_key)
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(prompt, mode, level, mood)},
        ],
    )
    return _parse(response.choices[0].message.content)
