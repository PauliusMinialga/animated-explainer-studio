"""Deterministic Manim script generation for a single animation phase.

Each phase gets a clean canvas with only its own nodes and edges.
No cross-phase clutter; no arrows overlapping unrelated nodes.

Scene layout per phase:
  - Title bar at top: "repo_name  |  Phase N/T: Phase Title"
  - Central repo node at origin
  - Phase nodes radially arranged, scaled to fit cleanly
  - Edges only between nodes present in this phase
  - Global-view highlight at end (all nodes pulse)
"""

import math

_NODE_COLORS = [
    "GOLD_D", "GREEN_D", "TEAL_D", "PURPLE_D",
    "RED_D", "MAROON_D", "ORANGE", "PINK",
    "BLUE_D", "YELLOW_D",
]

_TITLE_Y      =  3.5
_STEP_LABEL_Y = -3.5
_MAX_RADIUS   =  2.8


def _node_size(n: int) -> tuple[float, float, int]:
    if n <= 3:
        return 2.6, 1.0, 19
    elif n <= 5:
        return 2.2, 0.85, 17
    else:
        return 1.9, 0.75, 15


def render_phase_to_manim(
    repo_name: str,
    phase_num: int,
    total_phases: int,
    phase_title: str,
    nodes: list[dict],
    edges: list[dict],
    tts_info: str = "",
) -> str:
    """
    Generate one Manim scene for a single phase of a repo mind-map.

    Args:
        repo_name:     central node label
        phase_num:     1-based phase index
        total_phases:  total number of phases (for progress label)
        phase_title:   short title for this phase (shown in header)
        nodes:         list of {id, label} for this phase only
        edges:         list of {from, to} — only between nodes in this phase
        tts_info:      narration estimate for timing
    """
    if not nodes:
        return _minimal_scene(repo_name, phase_num, total_phases, phase_title)

    n = len(nodes)

    # ── Timing ────────────────────────────────────────────────────────────────
    words    = len(tts_info.split()) if tts_info else 30
    target_s = max(12.0, (words / 130) * 60 + 2)
    # steps: 1 title + 1 central + n nodes + n center-arrows + len(edges) inter-arrows + 1 global
    total_steps = 2 + n + n + len(edges) + 1
    step_time   = round(max(0.4, min(1.1, (target_s - 2.0) / max(total_steps, 1))), 2)
    wait_bt     = round(step_time * 0.22, 2)

    radius = round(min(_MAX_RADIUS, max(1.6, n * 0.5)), 4)
    rw, rh, fs = _node_size(n)

    header_text = f"{repo_name}  |  {phase_num}/{total_phases}: {phase_title}"

    lines = [
        "from manim import *",
        "import numpy as np",
        "",
        "",
        "class GeneratedScene(Scene):",
        "    def construct(self):",
        "",
        "        # ── Header ───────────────────────────────────────────────",
        f"        _header = Text({repr(header_text)}, font_size=20, color=GRAY_B)",
        f"        _header.move_to(np.array([0.0, {_TITLE_Y}, 0.0]))",
        f"        self.play(FadeIn(_header), run_time={step_time})",
        f"        self.wait({wait_bt})",
        "",
        "        # ── Central node ─────────────────────────────────────────",
        "        _c_rect = Rectangle(",
        "            width=2.6, height=1.0, fill_opacity=0.9,",
        "            fill_color=BLUE_E, stroke_color=WHITE, stroke_width=2,",
        "        )",
        f"        _c_text = Text({repr(repo_name)}, font_size=20, color=WHITE, weight=BOLD)",
        "        _c_text.move_to(_c_rect.get_center())",
        "        central = VGroup(_c_rect, _c_text).move_to(ORIGIN)",
        "        node_list = []",
        '        node_map = {"center": central}',
        "",
        f"        self.play(FadeIn(central), run_time={step_time})",
        f"        self.wait({wait_bt})",
        "",
    ]

    # ── Phase nodes ───────────────────────────────────────────────────────────
    for i, node in enumerate(nodes):
        color   = _NODE_COLORS[i % len(_NODE_COLORS)]
        angle   = 2 * math.pi * i / n
        x       = round(math.cos(angle) * radius, 4)
        y       = round(max(-3.0, min(3.0, math.sin(angle) * radius)), 4)
        label   = node.get("label", node.get("id", f"node{i}"))
        node_id = node.get("id", f"node{i}")

        lines += [
            f"        # {node_id}",
            f"        _r{i} = Rectangle(width={rw}, height={rh}, fill_opacity=0.85,",
            f"            fill_color={color}, stroke_color=WHITE, stroke_width=1.5)",
            f"        _t{i} = Text({repr(label)}, font_size={fs}, color=WHITE)",
            f"        _t{i}.move_to(_r{i}.get_center())",
            f"        _n{i} = VGroup(_r{i}, _t{i}).move_to(np.array([{x}, {y}, 0.0]))",
            f"        node_list.append(_n{i})",
            f"        node_map[{repr(node_id)}] = _n{i}",
            f"        self.play(FadeIn(_n{i}), run_time={step_time})",
            f"        self.wait({wait_bt})",
            "",
        ]

    # ── Center → phase-node arrows ────────────────────────────────────────────
    lines += [
        "        # ── Center arrows ────────────────────────────────────────",
        "        for _node in node_list:",
        "            _ca = Arrow(",
        "                start=central.get_center(), end=_node.get_center(),",
        "                buff=0.5, stroke_width=2.5, color=GRAY_B,",
        "                max_tip_length_to_length_ratio=0.15,",
        "            )",
        f"            self.play(GrowArrow(_ca), run_time={step_time})",
        f"            self.wait({wait_bt})",
        "",
        "        # ── Inter-node arrows ─────────────────────────────────────",
    ]

    for edge in edges:
        f_id = edge.get("from", "")
        t_id = edge.get("to", "")
        # Skip center↔center and edges where either end is the central node
        # (already covered by center arrows above)
        if f_id in ("center",) or t_id in ("center",):
            continue
        lines += [
            f"        if {repr(f_id)} in node_map and {repr(t_id)} in node_map:",
            f"            _ia = Arrow(",
            f"                start=node_map[{repr(f_id)}].get_center(),",
            f"                end=node_map[{repr(t_id)}].get_center(),",
            f"                buff=0.45, stroke_width=2.5, color=YELLOW_D,",
            f"                max_tip_length_to_length_ratio=0.15,",
            f"            )",
            f"            self.play(GrowArrow(_ia), run_time={step_time})",
            f"            self.wait({wait_bt})",
        ]

    # ── Global view: pulse everything ─────────────────────────────────────────
    global_wait = round(step_time * 1.4, 2)
    summary_text = f"Phase {phase_num}/{total_phases}: {phase_title}"
    lines += [
        "",
        "        # ── Global view ───────────────────────────────────────────",
        f"        _lbl = Text({repr(summary_text)}, font_size=17, color=YELLOW)",
        f"        _lbl.move_to(np.array([0.0, {_STEP_LABEL_Y}, 0.0]))",
        "        self.play(",
        "            FadeIn(_lbl),",
        "            *[_n.animate.set_stroke(color=WHITE, width=3) for _n in node_list],",
        f"            run_time={round(step_time * 0.8, 2)},",
        "        )",
        f"        self.wait({global_wait})",
    ]

    return "\n".join(lines)


# Keep old name as alias so any remaining callers don't break
def render_graph_to_manim(repo_name, nodes, edges, tts_info=""):
    return render_phase_to_manim(repo_name, 1, 1, repo_name, nodes, edges, tts_info)


def _minimal_scene(repo_name: str, phase_num: int, total_phases: int, phase_title: str) -> str:
    header = f"{repo_name}  |  {phase_num}/{total_phases}: {phase_title}"
    return (
        "from manim import *\n\n\n"
        "class GeneratedScene(Scene):\n"
        "    def construct(self):\n"
        f"        h = Text({repr(header)}, font_size=20, color=GRAY_B).move_to([0, 3.5, 0])\n"
        "        rect = Rectangle(width=3.2, height=1.2, fill_opacity=0.9, fill_color=BLUE_E)\n"
        f"        text = Text({repr(repo_name)}, font_size=26, color=WHITE)\n"
        "        text.move_to(rect.get_center())\n"
        "        self.play(FadeIn(h), FadeIn(VGroup(rect, text)))\n"
        "        self.wait(3)\n"
    )
