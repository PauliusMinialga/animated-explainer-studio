from manim import *


class TCPHandshake(Scene):
    def construct(self):

        # --- Intro: What is TCP? ---
        intro_title = Text("What is TCP?", font_size=40, color=BLUE)
        intro_title.to_edge(UP, buff=0.8)
        self.play(Write(intro_title))

        para1 = Text(
            "TCP (Transmission Control Protocol) is the set of rules\n"
            "computers follow to send data reliably over the internet.",
            font_size=22, line_spacing=1.2,
        )
        para2 = Text(
            "Before any data is sent, the two sides must first agree\n"
            'to connect. This agreement is called the "handshake".',
            font_size=22, line_spacing=1.2,
        )
        intro_lines = VGroup(para1, para2).arrange(DOWN, buff=0.5)
        intro_lines.next_to(intro_title, DOWN, buff=0.6)
        self.play(FadeIn(intro_lines, shift=UP, lag_ratio=0.3))
        self.wait(2)

        # Analogy
        analogy = Text(
            'Think of it like a phone call: you dial, they pick up, you say "hello".',
            font_size=20, color=YELLOW,
        )
        analogy.next_to(intro_lines, DOWN, buff=0.6)
        self.play(Write(analogy))
        self.wait(2)

        self.play(FadeOut(intro_title), FadeOut(intro_lines), FadeOut(analogy))
        self.wait(0.3)

        # --- Main scene: the handshake ---
        title = Text("The Three-Way Handshake", font_size=36)
        title.to_edge(UP)
        self.play(Write(title))

        # Create Client and Server with friendly labels
        client_box = RoundedRectangle(
            width=2.8, height=1.0, corner_radius=0.15,
            color=BLUE, fill_opacity=0.2,
        )
        client_label = Text("Your Computer", font_size=18, color=BLUE)
        client_sublabel = Text("(Client)", font_size=14, color=BLUE_C)
        client_text = VGroup(client_label, client_sublabel).arrange(DOWN, buff=0.05)
        client_icon = VGroup(client_box, client_text)
        client_icon.move_to(LEFT * 4 + UP * 2)

        server_box = RoundedRectangle(
            width=2.8, height=1.0, corner_radius=0.15,
            color=GREEN, fill_opacity=0.2,
        )
        server_label = Text("Website Server", font_size=18, color=GREEN)
        server_sublabel = Text("(Server)", font_size=14, color=GREEN_C)
        server_text = VGroup(server_label, server_sublabel).arrange(DOWN, buff=0.05)
        server_icon = VGroup(server_box, server_text)
        server_icon.move_to(RIGHT * 4 + UP * 2)

        self.play(FadeIn(client_icon), FadeIn(server_icon))
        self.wait(0.5)

        # Vertical timeline lines
        client_line = DashedLine(
            start=client_box.get_bottom() + DOWN * 0.1,
            end=client_box.get_bottom() + DOWN * 4.2,
            color=BLUE_D, dash_length=0.1,
        )
        server_line = DashedLine(
            start=server_box.get_bottom() + DOWN * 0.1,
            end=server_box.get_bottom() + DOWN * 4.2,
            color=GREEN_D, dash_length=0.1,
        )
        self.play(Create(client_line), Create(server_line))

        # Explanation box at bottom — reused for each step
        explain_box = RoundedRectangle(
            width=12, height=0.9, corner_radius=0.1,
            color=WHITE, fill_opacity=0.05, stroke_opacity=0.3,
        )
        explain_box.to_edge(DOWN, buff=0.2)

        # --- Step 1: SYN ---
        step1_num = Text("1", font_size=18, color=BLACK, weight=BOLD)
        step1_circle = Circle(radius=0.2, color=YELLOW, fill_opacity=1)
        step1_badge = VGroup(step1_circle, step1_num)
        step1_badge.move_to(LEFT * 6.2 + UP * 0.3)

        syn_arrow = Arrow(
            start=LEFT * 4 + UP * 0.3,
            end=RIGHT * 4 + DOWN * 0.1,
            color=YELLOW, buff=0,
            stroke_width=3,
        )
        syn_label = Text("SYN", font_size=22, color=YELLOW, weight=BOLD)
        syn_meaning = Text(
            '"Hey, can we connect?"',
            font_size=16, color=YELLOW_C,
        )
        syn_text = VGroup(syn_label, syn_meaning).arrange(DOWN, buff=0.08)
        syn_text.move_to(syn_arrow.get_center() + UP * 0.5)

        explain1 = Text(
            'SYN = "synchronize" — the client asks the server to start a connection',
            font_size=18, color=YELLOW,
        )
        explain1.move_to(explain_box.get_center())

        self.play(
            FadeIn(step1_badge),
            GrowArrow(syn_arrow),
            FadeIn(syn_text),
            FadeIn(explain_box),
            Write(explain1),
        )
        self.wait(2)

        # --- Step 2: SYN-ACK ---
        step2_num = Text("2", font_size=18, color=BLACK, weight=BOLD)
        step2_circle = Circle(radius=0.2, color=ORANGE, fill_opacity=1)
        step2_badge = VGroup(step2_circle, step2_num)
        step2_badge.move_to(RIGHT * 6.2 + DOWN * 0.8)

        syn_ack_arrow = Arrow(
            start=RIGHT * 4 + DOWN * 0.8,
            end=LEFT * 4 + DOWN * 1.2,
            color=ORANGE, buff=0,
            stroke_width=3,
        )
        syn_ack_label = Text("SYN-ACK", font_size=22, color=ORANGE, weight=BOLD)
        syn_ack_meaning = Text(
            '"Sure! I\'m ready too."',
            font_size=16, color=ORANGE,
        )
        syn_ack_text = VGroup(syn_ack_label, syn_ack_meaning).arrange(DOWN, buff=0.08)
        syn_ack_text.move_to(syn_ack_arrow.get_center() + UP * 0.5)

        explain2 = Text(
            'SYN-ACK = server confirms AND asks the client to confirm back',
            font_size=18, color=ORANGE,
        )
        explain2.move_to(explain_box.get_center())

        self.play(
            FadeIn(step2_badge),
            GrowArrow(syn_ack_arrow),
            FadeIn(syn_ack_text),
            Transform(explain1, explain2),
        )
        self.wait(2)

        # --- Step 3: ACK ---
        step3_num = Text("3", font_size=18, color=BLACK, weight=BOLD)
        step3_circle = Circle(radius=0.2, color=GREEN, fill_opacity=1)
        step3_badge = VGroup(step3_circle, step3_num)
        step3_badge.move_to(LEFT * 6.2 + DOWN * 1.9)

        ack_arrow = Arrow(
            start=LEFT * 4 + DOWN * 1.9,
            end=RIGHT * 4 + DOWN * 2.3,
            color=GREEN, buff=0,
            stroke_width=3,
        )
        ack_label = Text("ACK", font_size=22, color=GREEN, weight=BOLD)
        ack_meaning = Text(
            '"Got it, let\'s go!"',
            font_size=16, color=GREEN_C,
        )
        ack_text = VGroup(ack_label, ack_meaning).arrange(DOWN, buff=0.08)
        ack_text.move_to(ack_arrow.get_center() + UP * 0.5)

        explain3 = Text(
            'ACK = "acknowledge" — client confirms, connection is now open!',
            font_size=18, color=GREEN,
        )
        explain3.move_to(explain_box.get_center())

        self.play(
            FadeIn(step3_badge),
            GrowArrow(ack_arrow),
            FadeIn(ack_text),
            Transform(explain1, explain3),
        )
        self.wait(2)

        # --- Finale: clear the diagram and show summary ---
        all_diagram = VGroup(
            client_icon, server_icon,
            client_line, server_line,
            step1_badge, syn_arrow, syn_text,
            step2_badge, syn_ack_arrow, syn_ack_text,
            step3_badge, ack_arrow, ack_text,
            explain_box, explain1,
            title,
        )
        self.play(FadeOut(all_diagram))
        self.wait(0.3)

        # Summary screen
        summary_title = Text(
            "Connection Established!", font_size=42, color=GREEN,
        )
        summary_title.to_edge(UP, buff=1)
        self.play(Write(summary_title))

        summary_steps = VGroup(
            Text('1.  SYN        — "Can we connect?"', font_size=22, color=YELLOW),
            Text('2.  SYN-ACK — "Yes, I\'m ready too."', font_size=22, color=ORANGE),
            Text('3.  ACK         — "Great, let\'s go!"', font_size=22, color=GREEN),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        summary_steps.next_to(summary_title, DOWN, buff=0.8)
        self.play(FadeIn(summary_steps, lag_ratio=0.4))
        self.wait(1)

        summary_footer = Text(
            "Now the two computers can safely exchange data.",
            font_size=22, color=WHITE,
        )
        summary_footer.next_to(summary_steps, DOWN, buff=0.8)
        self.play(Write(summary_footer))
        self.wait(3)
