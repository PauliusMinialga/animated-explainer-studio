from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Title
        title = Text("Gitingest", font_size=48)
        subtitle = Text("GitHub Repository Ingestion Tool", font_size=24)
        subtitle.next_to(title, DOWN)
        self.play(Write(title), Write(subtitle))
        self.wait(0.5)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Main components
        components = VGroup(
            Text("Frontend", font_size=24),
            Text("Backend", font_size=24),
            Text("Git Integration", font_size=24),
            Text("Processing Engine", font_size=24)
        ).arrange(DOWN, buff=1)

        # Highlight components
        for component in components:
            self.play(Write(component))
            self.wait(0.3)

        # Arrows showing flow
        arrows = VGroup(
            Arrow(components[0].get_right(), components[1].get_left(), buff=0.4),
            Arrow(components[1].get_right(), components[2].get_left(), buff=0.4),
            Arrow(components[2].get_right(), components[3].get_left(), buff=0.4)
        )

        # Animate arrows sequentially
        for arrow in arrows:
            self.play(GrowArrow(arrow))
            self.wait(0.2)

        # Key features
        features = VGroup(
            Text("URL Transformation", font_size=20),
            Text("Pattern Matching", font_size=20),
            Text("File Size Control", font_size=20),
            Text("Private Repo Access", font_size=20)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        features.next_to(components, RIGHT, buff=2)

        # Connect features to components
        feature_arrows = VGroup(
            Arrow(features[0].get_left(), components[0].get_right(), buff=0.4),
            Arrow(features[1].get_left(), components[1].get_right(), buff=0.4),
            Arrow(features[2].get_left(), components[1].get_right(), buff=0.4),
            Arrow(features[3].get_left(), components[2].get_right(), buff=0.4)
        )

        # Animate features and connections
        for feature in features:
            self.play(Write(feature))
            self.wait(0.2)

        for arrow in feature_arrows:
            self.play(GrowArrow(arrow))
            self.wait(0.1)

        # Final summary
        summary = Text("Transform GitHub URLs into prompt-friendly text", font_size=20)
        summary.to_edge(DOWN)
        self.play(Write(summary))
        self.wait(2)
        self.play(FadeOut(components), FadeOut(arrows), FadeOut(features), FadeOut(feature_arrows), FadeOut(summary))