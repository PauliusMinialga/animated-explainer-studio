"""
Mistral script generation.

Given a prompt, returns:
- A Manim animation script (scene class `GeneratedScene`)
- A 3-part narration (intro / info / outro) matching Bote's TTSScript format

The intro and outro are spoken by the avatar (on-screen talking head).
The info part is the voiceover narrated during the Manim animation.
"""

import re
from dataclasses import dataclass, asdict
from mistralai.client import Mistral
from config import settings


@dataclass
class TTSScript:
    """Mirrors src/veed.py TTSScript — Bote consumes this for TTS + avatar."""
    intro: str
    info: str
    outro: str


_SYSTEM_PROMPT = """You are an expert Manim animator and computer science educator.

Given a topic or code snippet, experience level, and mood, return TWO things:
1. A complete, runnable Manim (Community Edition 0.20) Python script
2. A 3-part narration script:
   - INTRO: 1–2 sentences the avatar says on camera BEFORE the animation. Greet the viewer and introduce the topic.
   - INFO: The voiceover narrated DURING the animation. Explain what's appearing on screen step by step.
   - OUTRO: 1–2 sentences the avatar says on camera AFTER the animation. Summarize the takeaway.

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
- SurroundingRectangle ONLY accepts a single Mobject or VGroup — NEVER pass a Python list or slice
  WRONG: SurroundingRectangle(code_lines[0:3], ...)
  RIGHT: SurroundingRectangle(VGroup(*code_lines[0:3]), ...)
- VGroup slicing returns a list — always wrap with VGroup(*...) before passing to any Manim function
- Store each code line as a separate Text() variable; group with VGroup(...).arrange(DOWN, aligned_edge=LEFT)

SAFE MANIM OBJECTS (use only these unless you are 100% sure of the API):
- Text, VGroup, Arrow, Rectangle, Circle, Square, Line, Dot
- Axes (for graphs), NumberLine
- SurroundingRectangle (single Mobject/VGroup only — see rule above), Underline

NARRATION RULES:
- Plain spoken English, no markdown, no special characters
- INTRO: ~20 words, conversational greeting + topic introduction
- INFO: ~100–150 words, matches the visual timeline of the animation
- OUTRO: ~20 words, clear takeaway or summary

Return ONLY this exact format:

<manim_script>
[complete Python code]
</manim_script>

<intro>
[avatar intro speech]
</intro>

<info>
[animation voiceover]
</info>

<outro>
[avatar outro speech]
</outro>"""


def _build_user_prompt(prompt: str, mode: str, level: str, mood: str) -> str:
    return f"Mode: {mode}\nExperience level: {level}\nMood/tone: {mood}\n\nInput:\n{prompt}"


def _parse(content: str) -> dict:
    manim = re.search(r"<manim_script>\s*(.*?)\s*</manim_script>", content, re.DOTALL)
    intro = re.search(r"<intro>\s*(.*?)\s*</intro>", content, re.DOTALL)
    info = re.search(r"<info>\s*(.*?)\s*</info>", content, re.DOTALL)
    outro = re.search(r"<outro>\s*(.*?)\s*</outro>", content, re.DOTALL)

    if not manim:
        raise ValueError(f"Response missing <manim_script> tag.\nPreview:\n{content[:500]}")
    if not intro or not info or not outro:
        # Fallback: try old single <narration> tag and split heuristically
        narration = re.search(r"<narration>\s*(.*?)\s*</narration>", content, re.DOTALL)
        if narration:
            text = narration.group(1).strip()
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
            return {
                "manim_script": manim.group(1).strip(),
                "tts_script": TTSScript(
                    intro=sentences[0] if sentences else "",
                    info=" ".join(sentences[1:-1]) if len(sentences) > 2 else " ".join(sentences),
                    outro=sentences[-1] if len(sentences) > 1 else "",
                ),
            }
        raise ValueError(f"Response missing narration tags.\nPreview:\n{content[:500]}")

    return {
        "manim_script": manim.group(1).strip(),
        "tts_script": TTSScript(
            intro=intro.group(1).strip(),
            info=info.group(1).strip(),
            outro=outro.group(1).strip(),
        ),
    }


_REPO_PROMPT_TEMPLATE = """\
You are generating a Manim animation script for a short educational video about a GitHub repository.
The viewer is a {level} developer. Tone: {mood}.

Here is the repository content:
{repo_content}

─── ANIMATION STYLE: MIND MAP ───────────────────────────────────────────────
Create a mind map animation. Layout rules:
1. One central node (repo name) placed at ORIGIN using .move_to(ORIGIN)
2. 4–6 component nodes placed RADIALLY around the center using explicit coordinates:
   - Use .move_to(direction * distance) where direction is UP, DOWN, LEFT, RIGHT,
     UR, UL, DR, DL and distance is 2.5–3.5
   - Each node is a Rectangle with a Text label inside, grouped as VGroup(rect, label)
3. Arrows from center to each component node (CurvedArrow or Arrow)
4. For key interactions between components, add arrows BETWEEN component nodes too
5. Animate in this order:
   a. FadeIn the central node
   b. Create each component node one by one with a short self.wait(0.3) between each
   c. GrowArrow each connection from center outward
   d. GrowArrow the inter-component connections, highlighting the main data flow
   e. End with self.wait(2)

─── STRICT MANIM RULES (violations will crash the render) ────────────────────
- Scene class MUST be named exactly `GeneratedScene`
- Import only: `from manim import *`
- Do NOT use MathTex, Tex, Code(), BulletedList(), or any LaTeX
- Use Text() for all labels (font_size 20–28)
- Rectangle nodes: width=2.2, height=0.9, use color=BLUE or WHITE etc.
- NEVER use .arrange() for the mind map nodes — position each one with .move_to()
- SurroundingRectangle only accepts a single Mobject — wrap slices with VGroup(*...)
- Target 25–35 seconds total runtime
- Allowed objects: Text, VGroup, Arrow, CurvedArrow, Rectangle, Circle, Line,
  Dot, FadeIn, FadeOut, Create, Write, GrowArrow

─── OUTPUT FORMAT (return EXACTLY this, no extra text) ───────────────────────

--- MANIM_SCRIPT ---
[the complete Python script]

--- TTS_INTRO ---
[1 sentence: what this repo does]

--- TTS_INFO ---
[3-4 sentences, {mood} tone: main components, what each does,
 how they connect — follow the actual data/call flow in the code]

--- TTS_OUTRO ---
[1 sentence: key architectural pattern or takeaway]
"""

_REPO_SECTION_RE = re.compile(
    r"---\s*MANIM_SCRIPT\s*---\s*(.*?)\s*"
    r"---\s*TTS_INTRO\s*---\s*(.*?)\s*"
    r"---\s*TTS_INFO\s*---\s*(.*?)\s*"
    r"---\s*TTS_OUTRO\s*---\s*(.*?)(?:\s*---|$)",
    re.DOTALL,
)


def _parse_repo_response(content: str) -> tuple[str, TTSScript]:
    m = _REPO_SECTION_RE.search(content)
    if not m:
        raise ValueError(
            f"Repo response missing expected sections.\nPreview:\n{content[:600]}"
        )
    manim_script = m.group(1).strip()
    intro = m.group(2).strip()
    info = m.group(3).strip()
    outro = m.group(4).strip()
    return manim_script, TTSScript(intro=intro, info=info, outro=outro)


def generate_repo_scripts(
    url: str,
    repo_content: str,
    mood: str = "friendly",
    level: str = "beginner",
) -> tuple[str, TTSScript]:
    """
    Given pre-fetched repo content, generate a Manim script + TTSScript.

    Returns (manim_script: str, tts: TTSScript).
    Caller is responsible for fetching repo_content via ingest_github_repo().
    """
    if not settings.mistral_api_key:
        raise RuntimeError("MISTRAL_API_KEY is not set")

    user_prompt = _REPO_PROMPT_TEMPLATE.format(
        repo_content=repo_content,
        mood=mood,
        level=level,
    )

    client = Mistral(api_key=settings.mistral_api_key)
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": user_prompt}],
    )
    return _parse_repo_response(response.choices[0].message.content)


def generate_scripts(
    prompt: str,
    mode: str = "code",
    level: str = "beginner",
    mood: str = "friendly",
) -> dict:
    """Returns {"manim_script": str, "tts_script": TTSScript}."""
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
