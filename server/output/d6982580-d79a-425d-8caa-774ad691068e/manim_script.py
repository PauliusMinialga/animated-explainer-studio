from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Central node
        central_rect = Rectangle(
            width=2.2, height=0.9,
            fill_opacity=0.8, fill_color=BLUE, stroke_color=WHITE
        )
        central_text = Text("Gitingest", font_size=28)
        central_node = VGroup(central_rect, central_text).move_to(ORIGIN)

        # Component nodes
        components = {
            "HTML\nStructure": UP * 3,
            "Tailwind\nCSS": UR * 3,
            "JavaScript\nLogic": RIGHT * 3,
            "Form\nHandling": DR * 3,
            "API\nIntegration": DOWN * 3,
            "UI\nComponents": UL * 3
        }

        component_nodes = []
        for label, pos in components.items():
            rect = Rectangle(
                width=2.2, height=0.9,
                fill_opacity=0.8, fill_color=GOLD, stroke_color=WHITE
            )
            text = Text(label, font_size=20)
            node = VGroup(rect, text).move_to(pos)
            component_nodes.append(node)

        # Arrows from center to components
        center_arrows = []
        for node in component_nodes:
            arrow = Arrow(
                start=ORIGIN,
                end=node.get_center(),
                buff=0.2,
                stroke_width=4,
                color=GRAY
            )
            center_arrows.append(arrow)

        # Inter-component connections
        inter_arrows = [
            Arrow(
                start=component_nodes[0].get_center(),
                end=component_nodes[1].get_center(),
                buff=0.2,
                stroke_width=3,
                color=GREEN
            ),
            Arrow(
                start=component_nodes[1].get_center(),
                end=component_nodes[2].get_center(),
                buff=0.2,
                stroke_width=3,
                color=GREEN
            ),
            Arrow(
                start=component_nodes[2].get_center(),
                end=component_nodes[3].get_center(),
                buff=0.2,
                stroke_width=3,
                color=GREEN
            ),
            Arrow(
                start=component_nodes[3].get_center(),
                end=component_nodes[4].get_center(),
                buff=0.2,
                stroke_width=3,
                color=GREEN
            )
        ]

        # Animation sequence
        self.play(FadeIn(central_node))
        self.wait(0.5)

        for node in component_nodes:
            self.play(Create(node))
            self.wait(0.3)

        for arrow in center_arrows:
            self.play(GrowArrow(arrow))
            self.wait(0.2)

        for arrow in inter_arrows:
            self.play(GrowArrow(arrow))
            self.wait(0.2)

        self.wait(2)