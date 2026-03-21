"""
Mistral script generation.

Given a prompt, returns:
- A Manim animation script (scene class `GeneratedScene`)
- A 3-part narration (intro / info / outro) matching Bote's TTSScript format

The intro and outro are spoken by the avatar (on-screen talking head).
The info part is the voiceover narrated during the Manim animation.
"""

import json
import logging
import re
from dataclasses import dataclass
from config import settings
from .graph_renderer import render_phase_to_manim

logger = logging.getLogger(__name__)


# ── LLM client (Mistral) ──────────────────────────────────────────────────────

def _chat(system: str, user: str, temperature: float = 0.4) -> str:
    """Send a chat completion via Mistral and return the response text."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    from mistralai.client import Mistral
    if not settings.mistral_api_key:
        raise RuntimeError("No LLM key set — add MISTRAL_API_KEY to .env")
    client = Mistral(api_key=settings.mistral_api_key)
    resp = client.chat.complete(model="mistral-small-latest", messages=messages)
    logger.info("LLM: Mistral/mistral-small-latest")
    return resp.choices[0].message.content.strip()

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


_REPO_GRAPH_PROMPT = """\
You are analyzing a GitHub repository to produce a mind-map animation graph.
The target audience is a {level} developer. Tone: {mood}.

{repo_summary}

Identify 5–8 key components (modules, directories, services, key files) and \
the data/call-flow edges between them.

Return ONLY a valid JSON object — no markdown fences, no explanation:
{{
  "nodes": [
    {{"id": "snake_case_id", "label": "Short Label"}}
  ],
  "edges": [
    {{"from": "node_id", "to": "node_id"}}
  ],
  "tts": {{
    "intro": "1 sentence: what this repo does",
    "info": "5-8 sentences narrated DURING the animation. Describe each component and the flow between them in plain language, suitable for a beginner.",
    "outro": "1 sentence: key architectural pattern or takeaway"
  }}
}}

Rules:
- Do NOT include the repository itself as a node (it will be the central node automatically)
- 5–8 nodes total
- Edges show data/call flow, not directory nesting
- Labels: max 15 chars, no line breaks
- Return ONLY the raw JSON object, nothing else
"""

_PHASE_SPLITTER_PROMPT = """\
You are given a component graph for a software repository.
Split the nodes and edges into 2–4 logical animation phases.

Each phase focuses on one concern or layer (e.g. "Core", "Data Layer", "User Interaction").
The central repo node "{repo_name}" appears in ALL phases as the anchor.

Rules:
- 2–4 phases total, prefer 3
- Every non-central node must appear in exactly ONE phase
- A phase edge is only valid if BOTH its endpoints appear in that phase (or are the central node)
- Each phase title is 2–3 words
- Do not include edges that cross phases

Input graph:
{graph_json}

Return ONLY valid JSON — no markdown, no explanation:
{{
  "phases": [
    {{
      "title": "Phase title",
      "node_ids": ["id1", "id2"],
      "edges": [{{"from": "id1", "to": "id2"}}]
    }}
  ]
}}
"""


def _strip_json(raw: str) -> str:
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    return re.sub(r"\n?```$", "", raw.strip())


def generate_repo_scripts(
    url: str,
    repo_content: str,
    mood: str = "friendly",
    level: str = "beginner",
) -> tuple[list[str], TTSScript]:
    """
    Two-step LLM pipeline:
      1. Get the full component graph (nodes, edges, tts)
      2. Split the graph into logical phases

    Returns (manim_scripts: list[str], tts: TTSScript) — one script per phase.
    """
    m = re.search(r"github\.com/[^/]+/([^/\s]+)", url)
    repo_name = m.group(1) if m else url.rstrip("/").split("/")[-1]

    # ── Step 1: full graph ────────────────────────────────────────────────────
    logger.info("[repo-scripts] Step 1: generating component graph")
    raw_graph = _chat(
        system="You are a technical analyst. Return only valid JSON, no markdown.",
        user=_REPO_GRAPH_PROMPT.format(repo_summary=repo_content, mood=mood, level=level),
        temperature=0.3,
    )
    try:
        data = json.loads(_strip_json(raw_graph))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Step 1 LLM returned invalid JSON: {exc}\n\n{raw_graph[:400]}") from exc

    nodes: list[dict] = data.get("nodes", [])
    edges: list[dict] = data.get("edges", [])
    tts_data: dict = data.get("tts", {})
    tts = TTSScript(
        intro=tts_data.get("intro", ""),
        info=tts_data.get("info", ""),
        outro=tts_data.get("outro", ""),
    )

    # ── Step 2: phase splitter ────────────────────────────────────────────────
    logger.info("[repo-scripts] Step 2: splitting into phases")
    raw_phases = _chat(
        system="You are a technical animator. Return only valid JSON, no markdown.",
        user=_PHASE_SPLITTER_PROMPT.format(
            repo_name=repo_name,
            graph_json=json.dumps({"nodes": nodes, "edges": edges}, indent=2),
        ),
        temperature=0.2,
    )
    try:
        phases_data: list[dict] = json.loads(_strip_json(raw_phases)).get("phases", [])
    except json.JSONDecodeError as exc:
        logger.warning("Phase splitter returned invalid JSON, falling back to single phase: %s", exc)
        phases_data = [{"title": repo_name, "node_ids": [n["id"] for n in nodes], "edges": edges}]

    if not phases_data:
        phases_data = [{"title": repo_name, "node_ids": [n["id"] for n in nodes], "edges": edges}]

    # ── Build per-phase Manim scripts ─────────────────────────────────────────
    node_map = {n["id"]: n for n in nodes}
    total_phases = len(phases_data)
    # Spread TTS timing evenly across phases
    words_per_phase = max(10, len(tts.info.split()) // total_phases)
    phase_narration = " ".join(tts.info.split()[:words_per_phase * 2])  # rough estimate

    manim_scripts = []
    for i, phase in enumerate(phases_data):
        phase_node_ids: list[str] = phase.get("node_ids", [])
        phase_nodes = [node_map[nid] for nid in phase_node_ids if nid in node_map]
        valid_ids = set(phase_node_ids) | {"center"}
        phase_edges = [
            e for e in phase.get("edges", [])
            if e.get("from") in valid_ids and e.get("to") in valid_ids
        ]
        script = render_phase_to_manim(
            repo_name=repo_name,
            phase_num=i + 1,
            total_phases=total_phases,
            phase_title=phase.get("title", f"Part {i + 1}"),
            nodes=phase_nodes,
            edges=phase_edges,
            tts_info=phase_narration,
        )
        manim_scripts.append(script)
        logger.info(
            "[repo-scripts] Phase %d/%d — '%s' — %d nodes, %d edges",
            i + 1, total_phases, phase.get("title"), len(phase_nodes), len(phase_edges),
        )

    return manim_scripts, tts


def generate_scripts(
    prompt: str,
    mode: str = "code",
    level: str = "beginner",
    mood: str = "friendly",
) -> dict:
    """Returns {"manim_script": str, "tts_script": TTSScript}."""
    logger.info("Calling LLM via %s for concept/code script", settings.llm_provider)
    raw = _chat(
        system=_SYSTEM_PROMPT,
        user=_build_user_prompt(prompt, mode, level, mood),
        temperature=0.5,
    )
    return _parse(raw)
