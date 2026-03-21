from manim import *


class RecursionVisualization(Scene):
    def construct(self):

        title = Text("Recursion: Factorial(4)", font_size=36)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()

        # Show the code on the left
        code_text = Code(
            code_string=(
                "def factorial(n):\n"
                "    if n <= 1:\n"
                "        return 1\n"
                "    return n * factorial(n-1)"
            ),
            language="python",
            background="rectangle",
        ).scale(0.7)
        code_text.to_edge(LEFT, buff=0.5).shift(DOWN * 0.5)
        self.play(FadeIn(code_text))
        self.wait()

        # Build the call stack on the right
        stack_label = Text("Call Stack", font_size=24, color=YELLOW)
        stack_label.move_to(RIGHT * 3 + UP * 2.5)
        self.play(Write(stack_label))

        calls = ["factorial(4)", "factorial(3)", "factorial(2)", "factorial(1)"]
        colors = [BLUE, GREEN, ORANGE, RED]
        stack_frames = []

        # Push frames onto the stack
        for i, (call, color) in enumerate(zip(calls, colors)):
            frame = VGroup(
                RoundedRectangle(
                    width=3, height=0.7, corner_radius=0.1,
                    color=color, fill_opacity=0.3,
                ),
                Text(call, font_size=22, color=color),
            )
            frame.move_to(RIGHT * 3 + UP * (1.5 - i * 0.9))
            stack_frames.append(frame)

            push_label = Text("PUSH", font_size=16, color=GRAY)
            push_label.next_to(frame, LEFT, buff=0.3)
            self.play(FadeIn(frame, shift=DOWN), FadeIn(push_label))
            self.wait(0.3)
            self.play(FadeOut(push_label))

        # Base case highlight
        base_case = Text("Base case: return 1", font_size=20, color=RED)
        base_case.next_to(stack_frames[-1], DOWN, buff=0.5)
        self.play(Write(base_case))
        self.wait()
        self.play(FadeOut(base_case))

        # Pop frames and show return values
        return_values = ["1", "2 × 1 = 2", "3 × 2 = 6", "4 × 6 = 24"]

        for i in range(len(stack_frames) - 1, -1, -1):
            frame = stack_frames[i]
            ret_text = Text(
                f"→ {return_values[len(stack_frames) - 1 - i]}",
                font_size=20, color=YELLOW,
            )
            ret_text.next_to(frame, RIGHT, buff=0.3)
            self.play(Write(ret_text))
            self.wait(0.3)

            pop_label = Text("POP", font_size=16, color=GRAY)
            pop_label.next_to(frame, LEFT, buff=0.3)
            self.play(FadeIn(pop_label))
            self.play(
                FadeOut(frame, shift=UP),
                FadeOut(ret_text, shift=UP),
                FadeOut(pop_label),
            )

        # Final result
        result = Text("factorial(4) = 24", font_size=40, color=GREEN)
        result.move_to(RIGHT * 3)
        self.play(Write(result))
        self.wait(2)
