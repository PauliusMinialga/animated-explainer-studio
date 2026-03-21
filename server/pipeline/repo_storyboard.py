"""
Stage 2: Storyboard generation from Architecture.

Takes a structured Architecture and produces an ordered sequence of Scenes
that form a teaching progression: overview → flow → component focuses → recap.
"""

import json
import logging
import re

from .repo_models import Architecture, Storyboard, Scene, ScenePanel

logger = logging.getLogger(__name__)

_STORYBOARD_PROMPT = """\
You are an educational content designer creating an animated architecture walkthrough.

Given the following repository architecture, produce a storyboard: an ordered sequence
of 5–7 scenes that explain the system progressively.

Architecture:
{architecture_json}

Scene progression should follow this pattern:
1. Global overview — show all components, highlight the main ones
2. Main execution flow — step through the primary flow, highlighting each component in order
3–5. Component deep dives — focus on 2–3 key components or subsystems
6. Recap — show everything again with the main takeaway

For each scene, specify:
- which components are visible (all or a subset)
- which components are highlighted (the focus of that scene)
- which relationships are highlighted
- camera_mode: "fit" (show all) or "focus" (zoom into focus_component)
- narration: 2–3 sentences explaining what's shown
- panel: optional side information (title + bullet points)

Return ONLY valid JSON (no markdown fences):
{{
  "scenes": [
    {{
      "id": "scene_1",
      "title": "Scene Title",
      "goal": "What this scene teaches",
      "visible_components": ["comp_a", "comp_b"],
      "highlighted_components": ["comp_a"],
      "highlighted_relationships": ["rel_1"],
      "camera_mode": "fit",
      "focus_component": null,
      "narration": "Plain spoken English narration for this scene.",
      "panel": {{
        "title": "Panel Title",
        "bullets": ["Key point 1", "Key point 2"]
      }}
    }}
  ]
}}

Rules:
- 5–7 scenes total
- First scene is always the global overview (all components visible)
- Last scene is always a recap (all components visible, all highlighted)
- Narration: plain spoken English, no markdown, 2–3 sentences per scene
- Panel bullets: 2–4 short points
- All component/relationship IDs must match the architecture
- Return ONLY raw JSON
"""


def _strip_json(raw: str) -> str:
    raw = re.sub(r"^```[a-z]*\n?", "", raw.strip())
    return re.sub(r"\n?```$", "", raw.strip())


def generate_storyboard(architecture: Architecture) -> Storyboard:
    """Call Mistral to generate a teaching storyboard from the architecture."""
    from .scripts import _chat

    arch_json = architecture.model_dump(by_alias=True)

    logger.info("[repo-storyboard] Generating storyboard")
    raw = _chat(
        system="You are an educational designer. Return only valid JSON, no markdown.",
        user=_STORYBOARD_PROMPT.format(
            architecture_json=json.dumps(arch_json, indent=2),
        ),
        temperature=0.3,
    )

    try:
        data = json.loads(_strip_json(raw))
    except json.JSONDecodeError as exc:
        logger.warning("Storyboard LLM returned invalid JSON, using fallback: %s", exc)
        return _fallback_storyboard(architecture)

    scenes_data = data.get("scenes", [])
    if not scenes_data:
        return _fallback_storyboard(architecture)

    valid_comp_ids = {c.id for c in architecture.components}
    valid_rel_ids = {r.id for r in architecture.relationships}

    scenes = []
    for i, s in enumerate(scenes_data):
        scene = Scene(
            id=s.get("id", f"scene_{i}"),
            title=s.get("title", f"Scene {i + 1}"),
            goal=s.get("goal", ""),
            visible_components=[c for c in s.get("visible_components", []) if c in valid_comp_ids],
            highlighted_components=[c for c in s.get("highlighted_components", []) if c in valid_comp_ids],
            highlighted_relationships=[r for r in s.get("highlighted_relationships", []) if r in valid_rel_ids],
            camera_mode=s.get("camera_mode", "fit"),
            focus_component=s.get("focus_component") if s.get("focus_component") in valid_comp_ids else None,
            narration=s.get("narration", ""),
            panel=ScenePanel(**s["panel"]) if s.get("panel") else None,
        )
        # Ensure visible_components is not empty — show all if unspecified
        if not scene.visible_components:
            scene.visible_components = list(valid_comp_ids)
        scenes.append(scene)

    storyboard = Storyboard(scenes=scenes)
    logger.info("[repo-storyboard] Generated %d scenes", len(storyboard.scenes))
    return storyboard


def _fallback_storyboard(arch: Architecture) -> Storyboard:
    """Deterministic fallback if LLM storyboard fails."""
    all_ids = [c.id for c in arch.components]
    all_rel_ids = [r.id for r in arch.relationships]

    scenes = [
        Scene(
            id="overview",
            title="Project Overview",
            goal="Introduce all components at a high level",
            visible_components=all_ids,
            highlighted_components=all_ids[:3],
            highlighted_relationships=all_rel_ids[:3],
            camera_mode="fit",
            narration=f"{arch.repo_name} is composed of {len(arch.components)} main components. {arch.summary}",
            panel=ScenePanel(
                title="Architecture",
                bullets=[c.responsibility or c.label for c in arch.components[:4]],
            ),
        ),
    ]

    # Add a focus scene for each component (up to 4)
    for c in arch.components[:4]:
        related_rels = [
            r.id for r in arch.relationships
            if r.source == c.id or r.target == c.id
        ]
        connected = set()
        for r in arch.relationships:
            if r.source == c.id:
                connected.add(r.target)
            elif r.target == c.id:
                connected.add(r.source)

        scenes.append(Scene(
            id=f"focus_{c.id}",
            title=c.label,
            goal=f"Understand the {c.label} component",
            visible_components=list({c.id} | connected),
            highlighted_components=[c.id],
            highlighted_relationships=related_rels[:3],
            camera_mode="focus",
            focus_component=c.id,
            narration=c.responsibility or f"The {c.label} component handles a key part of the system.",
            panel=ScenePanel(
                title=c.label,
                bullets=[f"Type: {c.type}"] + ([f"Files: {', '.join(c.paths[:3])}"] if c.paths else []),
            ),
        ))

    scenes.append(Scene(
        id="recap",
        title="Recap",
        goal="Summarize the full architecture",
        visible_components=all_ids,
        highlighted_components=all_ids,
        highlighted_relationships=all_rel_ids,
        camera_mode="fit",
        narration=f"That's the full picture of {arch.repo_name}. {arch.summary}",
        panel=ScenePanel(
            title="Key Takeaways",
            bullets=[
                f"{len(arch.components)} components",
                f"{len(arch.relationships)} connections",
                arch.flows[0].title if arch.flows else "End-to-end flow",
            ],
        ),
    ))

    return Storyboard(scenes=scenes)
