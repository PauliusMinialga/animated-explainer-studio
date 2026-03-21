from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Central node
        central_text = Text("Gitingest", font_size=36, color=WHITE)
        central_rect = Rectangle(
            width=4.0,
            height=1.5,
            color=BLUE,
            fill_opacity=0.8,
            fill_color=BLUE_D
        )
        central_node = VGroup(central_rect, central_text).move_to(ORIGIN)
        self.play(FadeIn(central_node))
        self.wait(0.5)

        # Component nodes positions
        positions = {
            "HTML": RIGHT * 3,
            "Tailwind": UR * 3,
            "JavaScript": UP * 3,
            "Backend": UL * 3,
            "Metadata": LEFT * 3,
            "Deployment": DOWN * 3
        }

        # Create component nodes
        components = {}
        colors = [GREEN, YELLOW, PURPLE, ORANGE, TEAL, PINK]

        for i, (name, pos) in enumerate(positions.items()):
            rect = Rectangle(
                width=2.2,
                height=0.9,
                color=WHITE,
                fill_opacity=0.8,
                fill_color=colors[i]
            )
            text = Text(name, font_size=24, color=WHITE)
            node = VGroup(rect, text).move_to(pos)
            components[name] = node
            self.play(FadeIn(node))
            self.wait(0.3)

        # Create arrows from center to components
        center_to_components = {}
        for name, node in components.items():
            arrow = GrowArrow(
                Arrow(
                    start=central_node.get_right(),
                    end=node.get_left(),
                    buff=0.5,
                    stroke_width=4,
                    color=GRAY
                )
            )
            center_to_components[name] = arrow
            self.play(Create(arrow))
            self.wait(0.2)

        # Inter-component connections
        html_to_js = GrowArrow(
            CurvedArrow(
                components["HTML"].get_right(),
                components["JavaScript"].get_left(),
                angle=-PI/4,
                stroke_width=3,
                color=GRAY
            )
        )
        js_to_backend = GrowArrow(
            CurvedArrow(
                components["JavaScript"].get_top(),
                components["Backend"].get_bottom(),
                angle=PI/4,
                stroke_width=3,
                color=GRAY
            )
        )
        backend_to_metadata = GrowArrow(
            CurvedArrow(
                components["Backend"].get_left(),
                components["Metadata"].get_right(),
                angle=PI/2,
                stroke_width=3,
                color=GRAY
            )
        )
        metadata_to_deploy = GrowArrow(
            CurvedArrow(
                components["Metadata"].get_bottom(),
                components["Deployment"].get_top(),
                angle=PI/4,
                stroke_width=3,
                color=GRAY
            )
        )

        # Animate inter-component connections
        self.play(
            Create(html_to_js),
            Create(js_to_backend),
            Create(backend_to_metadata),
            Create(metadata_to_deploy)
        )
        self.wait(2)