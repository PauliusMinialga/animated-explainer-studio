"""
Mistral script generation.

Given a prompt, returns a Manim animation script and a narration text.
The Manim scene class is always named `GeneratedScene`.
"""

import re
from mistralai.client import Mistral
from config import settings

_SYSTEM_PROMPT = """You are an expert Manim animator and computer science educator.

Given a topic or code snippet, experience level, and mood, return TWO things:
1. A complete, runnable Manim (Community Edition 0.20) Python script
2. A narration text to be read aloud while the animation plays

MANIM RULES (follow EXACTLY — any violation will crash the render):
- The Scene class MUST be named exactly `GeneratedScene`
- Import only: `from manim import *`
- Do NOT use MathTex, Tex, or any LaTeX — use Text() for ALL text
- Do NOT use the Code() class — display code snippets using Text() with font="Courier New"
  Example: Text("def factorial(n):", font="Courier New", font_size=24)
  For multi-line code: stack multiple Text() objects in a VGroup with .arrange(DOWN, aligned_edge=LEFT)
- Do NOT use external images or custom fonts other than "Courier New"
- Do NOT use BulletedList() — use VGroup of Text() objects instead
- Target 30–45 seconds total runtime; keep it tight
- Use clear colours: WHITE, YELLOW, BLUE, GREEN, RED on dark background
- Show one concept at a time with labels and annotations
- ALWAYS call self.wait(1) between major steps
- Keep animations simple: Write, FadeIn, FadeOut, Create, GrowArrow, Transform

SAFE MANIM OBJECTS (use only these unless you are 100% sure of the API):
- Text, VGroup, Arrow, Rectangle, Circle, Square, Line, Dot
- Axes (for graphs), NumberLine
- SurroundingRectangle, Underline

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
