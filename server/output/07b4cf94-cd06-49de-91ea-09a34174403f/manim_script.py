from manim import *
import numpy as np


class GeneratedScene(Scene):
    def construct(self):
        # ── Central node ──────────────────────────────────────────
        _c_rect = Rectangle(
            width=2.6, height=1.0, fill_opacity=0.9,
            fill_color=BLUE_E, stroke_color=WHITE, stroke_width=2,
        )
        _c_text = Text('42_fdf', font_size=22, color=WHITE)
        _c_text.move_to(_c_rect.get_center())
        central = VGroup(_c_rect, _c_text).move_to(ORIGIN)
        node_list = []
        node_map = {"center": central}

        # node: minilibx
        _r0 = Rectangle(
            width=2.4, height=0.9, fill_opacity=0.85,
            fill_color=GOLD_D, stroke_color=WHITE, stroke_width=1.5,
        )
        _t0 = Text('MinilibX\n(window/pixel)', font_size=18, color=WHITE)
        _t0.move_to(_r0.get_center())
        _n0 = VGroup(_r0, _t0).move_to(np.array([3.85, 0.0, 0.0]))
        node_list.append(_n0)
        node_map['minilibx'] = _n0

        # node: fdf_core
        _r1 = Rectangle(
            width=2.4, height=0.9, fill_opacity=0.85,
            fill_color=GREEN_D, stroke_color=WHITE, stroke_width=1.5,
        )
        _t1 = Text('fdf_core\n(main logic)', font_size=18, color=WHITE)
        _t1.move_to(_r1.get_center())
        _n1 = VGroup(_r1, _t1).move_to(np.array([2.4004, 3.0101, 0.0]))
        node_list.append(_n1)
        node_map['fdf_core'] = _n1

        # node: parser
        _r2 = Rectangle(
            width=2.4, height=0.9, fill_opacity=0.85,
            fill_color=TEAL_D, stroke_color=WHITE, stroke_width=1.5,
        )
        _t2 = Text('parser\n(.fdf files)', font_size=18, color=WHITE)
        _t2.move_to(_r2.get_center())
        _n2 = VGroup(_r2, _t2).move_to(np.array([-0.8567, 3.7535, 0.0]))
        node_list.append(_n2)
        node_map['parser'] = _n2

        # node: renderer
        _r3 = Rectangle(
            width=2.4, height=0.9, fill_opacity=0.85,
            fill_color=PURPLE_D, stroke_color=WHITE, stroke_width=1.5,
        )
        _t3 = Text('renderer\n(wireframe draw)', font_size=18, color=WHITE)
        _t3.move_to(_r3.get_center())
        _n3 = VGroup(_r3, _t3).move_to(np.array([-3.4687, 1.6705, 0.0]))
        node_list.append(_n3)
        node_map['renderer'] = _n3

        # node: controls
        _r4 = Rectangle(
            width=2.4, height=0.9, fill_opacity=0.85,
            fill_color=RED_D, stroke_color=WHITE, stroke_width=1.5,
        )
        _t4 = Text('controls\n(user input)', font_size=18, color=WHITE)
        _t4.move_to(_r4.get_center())
        _n4 = VGroup(_r4, _t4).move_to(np.array([-3.4687, -1.6705, 0.0]))
        node_list.append(_n4)
        node_map['controls'] = _n4

        # node: color_manager
        _r5 = Rectangle(
            width=2.4, height=0.9, fill_opacity=0.85,
            fill_color=MAROON_D, stroke_color=WHITE, stroke_width=1.5,
        )
        _t5 = Text('color_manager\n(palette logic)', font_size=18, color=WHITE)
        _t5.move_to(_r5.get_center())
        _n5 = VGroup(_r5, _t5).move_to(np.array([-0.8567, -3.7535, 0.0]))
        node_list.append(_n5)
        node_map['color_manager'] = _n5

        # node: maps
        _r6 = Rectangle(
            width=2.4, height=0.9, fill_opacity=0.85,
            fill_color=ORANGE, stroke_color=WHITE, stroke_width=1.5,
        )
        _t6 = Text('maps\n(test terrain)', font_size=18, color=WHITE)
        _t6.move_to(_r6.get_center())
        _n6 = VGroup(_r6, _t6).move_to(np.array([2.4004, -3.0101, 0.0]))
        node_list.append(_n6)
        node_map['maps'] = _n6

        # ── Center → component arrows ─────────────────────────────
        center_arrows = []
        for _node in node_list:
            center_arrows.append(Arrow(
                start=central.get_center(),
                end=_node.get_center(),
                buff=0.6,
                stroke_width=2.5,
                color=GRAY_B,
                max_tip_length_to_length_ratio=0.15,
            ))

        # ── Inter-component arrows ────────────────────────────────
        inter_arrows = []
        if 'parser' in node_map and 'fdf_core' in node_map:
            inter_arrows.append(Arrow(
                start=node_map['parser'].get_center(),
                end=node_map['fdf_core'].get_center(),
                buff=0.55,
                stroke_width=2.5,
                color=YELLOW_D,
                max_tip_length_to_length_ratio=0.15,
            ))
        if 'fdf_core' in node_map and 'renderer' in node_map:
            inter_arrows.append(Arrow(
                start=node_map['fdf_core'].get_center(),
                end=node_map['renderer'].get_center(),
                buff=0.55,
                stroke_width=2.5,
                color=YELLOW_D,
                max_tip_length_to_length_ratio=0.15,
            ))
        if 'controls' in node_map and 'fdf_core' in node_map:
            inter_arrows.append(Arrow(
                start=node_map['controls'].get_center(),
                end=node_map['fdf_core'].get_center(),
                buff=0.55,
                stroke_width=2.5,
                color=YELLOW_D,
                max_tip_length_to_length_ratio=0.15,
            ))
        if 'fdf_core' in node_map and 'color_manager' in node_map:
            inter_arrows.append(Arrow(
                start=node_map['fdf_core'].get_center(),
                end=node_map['color_manager'].get_center(),
                buff=0.55,
                stroke_width=2.5,
                color=YELLOW_D,
                max_tip_length_to_length_ratio=0.15,
            ))
        if 'renderer' in node_map and 'minilibx' in node_map:
            inter_arrows.append(Arrow(
                start=node_map['renderer'].get_center(),
                end=node_map['minilibx'].get_center(),
                buff=0.55,
                stroke_width=2.5,
                color=YELLOW_D,
                max_tip_length_to_length_ratio=0.15,
            ))
        if 'color_manager' in node_map and 'renderer' in node_map:
            inter_arrows.append(Arrow(
                start=node_map['color_manager'].get_center(),
                end=node_map['renderer'].get_center(),
                buff=0.55,
                stroke_width=2.5,
                color=YELLOW_D,
                max_tip_length_to_length_ratio=0.15,
            ))
        if 'maps' in node_map and 'parser' in node_map:
            inter_arrows.append(Arrow(
                start=node_map['maps'].get_center(),
                end=node_map['parser'].get_center(),
                buff=0.55,
                stroke_width=2.5,
                color=YELLOW_D,
                max_tip_length_to_length_ratio=0.15,
            ))

        # ── Animation sequence ────────────────────────────────────
        self.play(FadeIn(central))
        self.wait(0.4)
        for _node in node_list:
            self.play(FadeIn(_node), run_time=0.35)
        self.wait(0.3)
        for _arrow in center_arrows:
            self.play(GrowArrow(_arrow), run_time=0.25)
        self.wait(0.4)
        for _arrow in inter_arrows:
            self.play(GrowArrow(_arrow), run_time=0.35)
        self.wait(2)