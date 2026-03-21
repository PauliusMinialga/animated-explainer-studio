"""Deterministic Manim script generation from a repo component graph.

Takes structured node/edge data (produced by the LLM as JSON) and renders
a valid, crash-proof Manim scene — no LLM writes Manim code here.

Scene structure:
  Phase 0 — Title card (repo name, centre)
  Phase 1 — Central node fades in
  Phase 2 — Component nodes appear one-by-one (radially)
  Phase 3 — Center → component arrows drawn one-by-one
  Phase 4 — Inter-component arrows drawn one-by-one
  Phase 5 — Global view: brief pulse / highlight of everything (outro avatar speaks here)
"""

import math

_NODE_COLORS = [
    "GOLD_D", "GREEN_D", "TEAL_D", "PURPLE_D",
    "RED_D", "MAROON_D", "ORANGE", "PINK",
]

# Manim frame: width=14.22, height=8.0  →  safe y ∈ [-3.5, 3.5], x ∈ [-6.5, 6.5]
_MAX_RADIUS   = 2.8   # nodes never exceed this radius from centre
_TITLE_Y      = 3.6   # title sits above the graph
_STEP_LABEL_Y = -3.6  # step label sits below


def _node_size(n: int) -> tuple[float, float, int]:
    """Return (rect_width, rect_height, font_size) scaled for node count."""
    if n <= 5:
        return 2.4, 0.9, 18
    elif n <= 8:
        return 2.0, 0.75, 16
    else:
        return 1.7, 0.65, 14


def render_graph_to_manim(
    repo_name: str,
    nodes: list[dict],
    edges: list[dict],
    tts_info: str = "",
) -> str:
    """
    Generate a deterministic Manim scene for a repo mind map.

    Args:
        repo_name: displayed as the central node label
        nodes: list of {id: str, label: str} — component nodes
        edges: list of {from: str, to: str} — "center" is a valid node id
        tts_info: the narration spoken during the animation (used to estimate duration)
    """
    if not nodes:
        return _minimal_scene(repo_name)

    n = len(nodes)

    # ── Timing: target animation duration = estimated TTS speech duration ─────
    words = len(tts_info.split()) if tts_info else 40
    target_s = max(15.0, (words / 130) * 60 + 3)

    n_edges = len(edges)
    # phases: 1 (title) + 1 (central) + n (nodes) + n (center arrows) + n_edges (inter-arrows) + 1 (global view)
    total_steps = 2 + n + n + n_edges + 1
    available   = max(target_s - 3.0, 10.0)
    step_time   = round(available / max(total_steps, 1), 2)
    step_time   = max(0.4, min(step_time, 1.2))
    wait_between = round(step_time * 0.25, 2)

    # Radius: spread nodes evenly but stay within safe zone
    # For small n use full radius; for large n scale down so nodes don't overlap
    radius = min(_MAX_RADIUS, max(1.8, n * 0.42))
    radius = round(radius, 4)

    rw, rh, fs = _node_size(n)

    lines = [
        "from manim import *",
        "import numpy as np",
        "",
        "",
        "class GeneratedScene(Scene):",
        "    def construct(self):",
        "",
        "        # ── Phase 0: Title ────────────────────────────────────────",
        f"        _title = Text({repr(repo_name)}, font_size=28, color=WHITE, weight=BOLD)",
        f"        _title.move_to(np.array([0.0, {_TITLE_Y}, 0.0]))",
        f"        self.play(FadeIn(_title), run_time={step_time})",
        f"        self.wait({wait_between})",
        "",
        "        # ── Phase 1: Central node ─────────────────────────────────",
        "        _c_rect = Rectangle(",
        "            width=2.6, height=1.0, fill_opacity=0.9,",
        "            fill_color=BLUE_E, stroke_color=WHITE, stroke_width=2,",
        "        )",
        f"        _c_text = Text({repr(repo_name)}, font_size=20, color=WHITE)",
        "        _c_text.move_to(_c_rect.get_center())",
        "        central = VGroup(_c_rect, _c_text).move_to(ORIGIN)",
        "        node_list = []",
        '        node_map = {"center": central}',
        "",
        f"        self.play(FadeIn(central), run_time={step_time})",
        f"        self.wait({wait_between})",
        "",
    ]

    # Component nodes — radially placed, clamped to safe zone
    for i, node in enumerate(nodes):
        color  = _NODE_COLORS[i % len(_NODE_COLORS)]
        angle  = 2 * math.pi * i / n
        x      = round(math.cos(angle) * radius, 4)
        y      = round(math.sin(angle) * radius, 4)
        # Clamp y so title and step label don't collide
        y      = round(max(-3.0, min(3.0, y)), 4)
        label  = node.get("label", node.get("id", f"node{i}"))
        node_id = node.get("id", f"node{i}")

        lines += [
            f"        # node: {node_id}",
            f"        _r{i} = Rectangle(",
            f"            width={rw}, height={rh}, fill_opacity=0.85,",
            f"            fill_color={color}, stroke_color=WHITE, stroke_width=1.5,",
            f"        )",
            f"        _t{i} = Text({repr(label)}, font_size={fs}, color=WHITE)",
            f"        _t{i}.move_to(_r{i}.get_center())",
            f"        _n{i} = VGroup(_r{i}, _t{i}).move_to(np.array([{x}, {y}, 0.0]))",
            f"        node_list.append(_n{i})",
            f"        node_map[{repr(node_id)}] = _n{i}",
            "",
        ]

    lines += [
        "        # ── Phase 2: Component nodes appear one by one ───────────",
    ]
    for i in range(n):
        lines += [
            f"        self.play(FadeIn(_n{i}), run_time={step_time})",
            f"        self.wait({wait_between})",
        ]

    # Center → component arrows
    lines += [
        "",
        "        # ── Phase 3: Center → component arrows ───────────────────",
        "        center_arrows = []",
        "        for _node in node_list:",
        "            _arr = Arrow(",
        "                start=central.get_center(),",
        "                end=_node.get_center(),",
        "                buff=0.55,",
        "                stroke_width=2.5,",
        "                color=GRAY_B,",
        "                max_tip_length_to_length_ratio=0.15,",
        "            )",
        "            center_arrows.append(_arr)",
        f"            self.play(GrowArrow(_arr), run_time={step_time})",
        f"            self.wait({wait_between})",
        "",
        "        # ── Phase 4: Inter-component arrows ───────────────────────",
        "        inter_arrows = []",
    ]

    for edge in edges:
        from_id = edge.get("from", "")
        to_id   = edge.get("to", "")
        lines += [
            f"        if {repr(from_id)} in node_map and {repr(to_id)} in node_map:",
            f"            _ia = Arrow(",
            f"                start=node_map[{repr(from_id)}].get_center(),",
            f"                end=node_map[{repr(to_id)}].get_center(),",
            f"                buff=0.5,",
            f"                stroke_width=2.5,",
            f"                color=YELLOW_D,",
            f"                max_tip_length_to_length_ratio=0.15,",
            f"            )",
            f"            inter_arrows.append(_ia)",
            f"            self.play(GrowArrow(_ia), run_time={step_time})",
            f"            self.wait({wait_between})",
        ]

    # Global view phase — highlight everything simultaneously
    global_wait = round(step_time * 1.5, 2)
    lines += [
        "",
        "        # ── Phase 5: Global view (all components visible) ────────",
        "        _summary = Text(",
        f"            {repr(f'Architecture: {repo_name}')},",
        "            font_size=16, color=YELLOW,",
        "        )",
        f"        _summary.move_to(np.array([0.0, {_STEP_LABEL_Y}, 0.0]))",
        "        self.play(",
        "            FadeIn(_summary),",
        "            *[_n.animate.set_color(WHITE) for _n in node_list],",
        f"            run_time={round(step_time * 0.8, 2)},",
        "        )",
        f"        self.wait({global_wait})",
    ]

    return "\n".join(lines)


def _minimal_scene(repo_name: str) -> str:
    return (
        "from manim import *\n\n\n"
        "class GeneratedScene(Scene):\n"
        "    def construct(self):\n"
        "        rect = Rectangle(width=3.2, height=1.2, fill_opacity=0.9, fill_color=BLUE_E)\n"
        f"        text = Text({repr(repo_name)}, font_size=28, color=WHITE)\n"
        "        text.move_to(rect.get_center())\n"
        "        self.play(FadeIn(VGroup(rect, text)))\n"
        "        self.wait(3)\n"
    )
