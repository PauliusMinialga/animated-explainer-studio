"""Deterministic Manim script generation from a repo component graph.

Takes structured node/edge data (produced by Mistral as JSON) and renders
a valid, crash-proof Manim scene — no LLM writes Manim code here.
"""

import math

_NODE_COLORS = [
    "GOLD_D", "GREEN_D", "TEAL_D", "PURPLE_D",
    "RED_D", "MAROON_D", "ORANGE", "PINK",
]


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
    # Average speech rate ~130 wpm. Add 3s padding at end for avatar transition.
    words = len(tts_info.split()) if tts_info else 40
    target_s = max(15.0, (words / 130) * 60 + 3)

    # Budget per phase (seconds):
    #   Phase 1 — central node fade in:   1 step
    #   Phase 2 — component nodes:        n steps
    #   Phase 3 — center arrows:          n steps
    #   Phase 4 — inter-component arrows: len(edges) steps
    #   Final wait:                        2s fixed
    n_edges = len(edges)
    total_steps = 1 + n + n + n_edges
    available = max(target_s - 2.0, 10.0)
    step_time = round(available / max(total_steps, 1), 2)
    step_time = max(0.4, min(step_time, 1.2))  # clamp: 0.4s–1.2s per step
    wait_between = round(step_time * 0.3, 2)

    radius = max(3.0, n * 0.55)

    lines = [
        "from manim import *",
        "import numpy as np",
        "",
        "",
        "class GeneratedScene(Scene):",
        "    def construct(self):",
        "        # ── Central node ──────────────────────────────────────────",
        "        _c_rect = Rectangle(",
        "            width=2.6, height=1.0, fill_opacity=0.9,",
        "            fill_color=BLUE_E, stroke_color=WHITE, stroke_width=2,",
        "        )",
        f"        _c_text = Text({repr(repo_name)}, font_size=22, color=WHITE)",
        "        _c_text.move_to(_c_rect.get_center())",
        "        central = VGroup(_c_rect, _c_text).move_to(ORIGIN)",
        "        node_list = []",
        '        node_map = {"center": central}',
        "",
    ]

    # Component nodes — radially placed
    for i, node in enumerate(nodes):
        color = _NODE_COLORS[i % len(_NODE_COLORS)]
        angle = 2 * math.pi * i / n
        x = round(math.cos(angle) * radius, 4)
        y = round(math.sin(angle) * radius, 4)
        label = node.get("label", node.get("id", f"node{i}"))
        node_id = node.get("id", f"node{i}")

        lines += [
            f"        # node: {node_id}",
            f"        _r{i} = Rectangle(",
            f"            width=2.4, height=0.9, fill_opacity=0.85,",
            f"            fill_color={color}, stroke_color=WHITE, stroke_width=1.5,",
            f"        )",
            f"        _t{i} = Text({repr(label)}, font_size=18, color=WHITE)",
            f"        _t{i}.move_to(_r{i}.get_center())",
            f"        _n{i} = VGroup(_r{i}, _t{i}).move_to(np.array([{x}, {y}, 0.0]))",
            f"        node_list.append(_n{i})",
            f"        node_map[{repr(node_id)}] = _n{i}",
            "",
        ]

    # Center → component arrows (one per component node, drawn via loop)
    lines += [
        "        # ── Center → component arrows ─────────────────────────────",
        "        center_arrows = []",
        "        for _node in node_list:",
        "            center_arrows.append(Arrow(",
        "                start=central.get_center(),",
        "                end=_node.get_center(),",
        "                buff=0.6,",
        "                stroke_width=2.5,",
        "                color=GRAY_B,",
        "                max_tip_length_to_length_ratio=0.15,",
        "            ))",
        "",
        "        # ── Inter-component arrows ────────────────────────────────",
        "        inter_arrows = []",
    ]

    for edge in edges:
        from_id = edge.get("from", "")
        to_id = edge.get("to", "")
        lines += [
            f"        if {repr(from_id)} in node_map and {repr(to_id)} in node_map:",
            f"            inter_arrows.append(Arrow(",
            f"                start=node_map[{repr(from_id)}].get_center(),",
            f"                end=node_map[{repr(to_id)}].get_center(),",
            f"                buff=0.55,",
            f"                stroke_width=2.5,",
            f"                color=YELLOW_D,",
            f"                max_tip_length_to_length_ratio=0.15,",
            f"            ))",
        ]

    lines += [
        "",
        "        # ── Animation sequence ────────────────────────────────────",
        f"        self.play(FadeIn(central), run_time={step_time})",
        f"        self.wait({wait_between})",
        "        for _node in node_list:",
        f"            self.play(FadeIn(_node), run_time={step_time})",
        f"            self.wait({wait_between})",
        "        for _arrow in center_arrows:",
        f"            self.play(GrowArrow(_arrow), run_time={step_time})",
        f"            self.wait({wait_between})",
        "        for _arrow in inter_arrows:",
        f"            self.play(GrowArrow(_arrow), run_time={step_time})",
        f"            self.wait({wait_between})",
        "        self.wait(2)",
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
