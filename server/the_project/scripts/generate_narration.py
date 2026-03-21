"""
Generate a timestamped narration script from a Manim scene's animation timeline.

The narration is co-located with the animation timing so they can't drift apart.
Each segment specifies: duration (seconds) and what to say during that time.

Usage:
    python scripts/generate_narration.py concepts/gradient_descent.py

Output: a JSON narration file with start/end times and text for each segment.
This can be fed to any TTS API (VEED, ElevenLabs, etc.) to generate audio.
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NarrationSegment:
    start: float
    end: float
    text: str


def gradient_descent_narration():
    """
    Narration timeline for GradientDescentVisualization.

    Each entry is (duration_seconds, narration_text).
    Durations match the Manim animation calls exactly:
    - self.play() = 1s by default
    - self.wait() = 1s by default
    - self.wait(n) = n seconds
    """
    timeline = [
        # Title appears (play + wait = 2s)
        (2.0, "Gradient descent is one of the most important optimization "
              "algorithms in machine learning. Let's see how it works."),

        # Axes + labels appear (play = 1s)
        (1.0, "We'll start with a simple function plotted on a graph."),

        # Graph + label drawn (play + wait = 2s)
        (2.0, "Here's f of x equals x squared — a parabola. "
              "The lowest point is at x equals zero."),

        # "Goal" text appears, stays, fades (play + wait + play = 3s)
        (3.0, "Our goal is to find the value of x that minimizes this function. "
              "Gradient descent does this iteratively, without needing to solve it analytically."),

        # Starting dot + label appear, label fades (play + wait + play = 3s)
        (3.0, "We start at a random point — here, x equals two point five. "
              "The function value is quite high up on the curve."),

        # Info box appears (play = 1s)
        (1.0, "Let's track each step in this info panel."),

        # Step 1 (play + play + play + play = 4s) — first step gets more explanation
        (4.0, "In step one, we compute the gradient — the slope of the curve at our "
              "current position. The orange line shows this tangent. "
              "We then move in the opposite direction of the gradient, "
              "scaled by the learning rate."),

        # Step 2 (4s)
        (4.0, "Step two — the gradient is smaller now because we're closer to "
              "the minimum. Notice the step size gets smaller too. "
              "That's the beauty of gradient descent — it naturally slows down "
              "as it approaches the answer."),

        # Step 3 (4s)
        (4.0, "Step three continues the pattern. Each iteration, we compute "
              "the slope, and take a step proportional to it. "
              "The learning rate of zero point three controls how big each step is."),

        # Step 4 (4s)
        (4.0, "We're getting close now. The gradient is much smaller, "
              "so our steps are tiny."),

        # Step 5 (4s)
        (4.0, "Step five — almost there. The dot is converging toward "
              "the bottom of the parabola."),

        # Step 6 (4s)
        (4.0, "The changes are barely visible now. We're very close to "
              "the minimum."),

        # Step 7 (4s)
        (4.0, "Step seven — essentially at the minimum. In practice, "
              "you'd set a threshold and stop when the gradient is small enough."),

        # Step 8 (4s)
        (4.0, "Final step. The algorithm has converged."),

        # Result text + final wait (play + wait(2) = 3s)
        (3.0, "And there it is — gradient descent found the minimum at "
              "x approximately equal to zero. This same algorithm, scaled up, "
              "is how neural networks learn their parameters."),
    ]

    segments = []
    current_time = 0.0
    for duration, text in timeline:
        segments.append(NarrationSegment(
            start=round(current_time, 2),
            end=round(current_time + duration, 2),
            text=text,
        ))
        current_time += duration

    return segments


def binary_search_narration():
    """
    Narration timeline for BinarySearchVisualization.

    Timing breakdown:
    - play(Create(squares), Write(labels)) = 1s
    - wait() = 1s
    - play(Create(left_arrow), Create(right_arrow)) = 1s
    Loop iteration 1 (mid=4, value=16 < 23, move left):
    - play(Create(mid_arrow)) = 1s
    - play(set_fill) = 1s
    - wait() = 1s
    - play(left_arrow move) = 1s
    - play(FadeOut(mid_arrow)) = 1s
    Loop iteration 2 (mid=6, value=38 > 23, move right):
    - play(Create(mid_arrow)) = 1s
    - play(set_fill) = 1s
    - wait() = 1s
    - play(right_arrow move) = 1s
    - play(FadeOut(mid_arrow)) = 1s
    Loop iteration 3 (mid=5, value=23 == target, found!):
    - play(Create(mid_arrow)) = 1s
    - play(set_fill) = 1s
    - wait() = 1s
    - play(Write(found)) = 1s
    - wait(2) = 2s
    Total = 18s
    """
    timeline = [
        # Array appears (play + wait = 2s)
        (2.0, "Here's a sorted array of numbers. We want to find "
              "the value twenty-three."),

        # Left and right pointers appear (play = 1s)
        (1.0, "We set two pointers — one at each end of the array."),

        # Iteration 1: mid=4 (value 16), check, move left (5s)
        (2.0, "We check the middle element. It's sixteen — "
              "that's less than twenty-three."),
        (2.0, "So we know twenty-three must be in the right half. "
              "We move the left pointer up."),
        (1.0, ""),

        # Iteration 2: mid=6 (value 38), check, move right (5s)
        (2.0, "The new middle is thirty-eight — that's too big."),
        (2.0, "So twenty-three must be in the left half. "
              "We move the right pointer down."),
        (1.0, ""),

        # Iteration 3: mid=5 (value 23), found! (5s)
        (2.0, "We check the middle again — it's twenty-three!"),
        (1.0, "Found it!"),
        (2.0, "Binary search found the target in just three steps, "
              "instead of checking all nine elements one by one."),
    ]

    segments = []
    current_time = 0.0
    for duration, text in timeline:
        segments.append(NarrationSegment(
            start=round(current_time, 2),
            end=round(current_time + duration, 2),
            text=text,
        ))
        current_time += duration

    return segments


def recursion_narration():
    """
    Narration timeline for RecursionVisualization.

    Timing breakdown:
    - play(Write(title)) = 1s
    - wait() = 1s
    - play(FadeIn(code_text)) = 1s
    - wait() = 1s
    - play(Write(stack_label)) = 1s
    Push loop (4 iterations × (play + wait(0.3) + play) = 4 × 2.3s = 9.2s)
    - play(Write(base_case)) = 1s
    - wait() = 1s
    - play(FadeOut(base_case)) = 1s
    Pop loop (4 iterations × (play + wait(0.3) + play + play) = 4 × 3.3s = 13.2s)
    - play(Write(result)) = 1s
    - wait(2) = 2s
    Total ≈ 33.4s
    """
    timeline = [
        # Title (play + wait = 2s)
        (2.0, "Let's see how recursion works by tracing through "
              "factorial of four."),

        # Code appears (play + wait = 2s)
        (2.0, "Here's the factorial function. It calls itself with "
              "a smaller number until it reaches the base case."),

        # Stack label (play = 1s)
        (1.0, "On the right, we'll build up the call stack."),

        # Push factorial(4) (2.3s)
        (2.3, "First, factorial of four is called. It needs factorial "
              "of three to compute its answer, so that goes on the stack."),

        # Push factorial(3) (2.3s)
        (2.3, "Factorial of three needs factorial of two."),

        # Push factorial(2) (2.3s)
        (2.3, "And factorial of two needs factorial of one."),

        # Push factorial(1) (2.3s)
        (2.3, "Factorial of one — this is the base case."),

        # Base case appears, waits, fades (3s)
        (3.0, "The base case returns one. Now the stack starts unwinding."),

        # Pop factorial(1) → 1 (3.3s)
        (3.3, "Factorial of one returns one."),

        # Pop factorial(2) → 2 (3.3s)
        (3.3, "Factorial of two multiplies two times one, giving two."),

        # Pop factorial(3) → 6 (3.3s)
        (3.3, "Factorial of three multiplies three times two, giving six."),

        # Pop factorial(4) → 24 (3.3s)
        (3.3, "And factorial of four multiplies four times six."),

        # Result (play + wait(2) = 3s)
        (3.0, "The final answer is twenty-four. Each call waited for the "
              "one below it to finish — that's recursion in action."),
    ]

    segments = []
    current_time = 0.0
    for duration, text in timeline:
        segments.append(NarrationSegment(
            start=round(current_time, 2),
            end=round(current_time + duration, 2),
            text=text,
        ))
        current_time += duration

    return segments


def explain_factorial_narration():
    """
    Narration timeline for ExplainFactorial.

    Timing breakdown:
    - play(Write(title)) + wait() = 2s
    - play(FadeIn(code)) + wait() = 2s
    - play(Create(highlight)) = 1s
    Line-by-line loop (4 iterations):
      i=0: play(Write(info)) + wait(1.5) = 2.5s
      i=1,2,3: play(Transform+FadeOut+Write) + wait(1.5) = 2.5s each
    Total loop = 10s
    - play(FadeOut) + wait(0.5) = 1.5s
    - play(code.animate.scale) = 1s
    - play(Write(trace_title)) = 1s
    Steps loop (7 iterations × (play + wait(0.5)) = 7 × 1.5s = 10.5s)
    - wait(2) = 2s
    Total ≈ 31.5s
    """
    timeline = [
        # Title + code appear (play + wait + play + wait = 4s)
        (4.0, "Let's walk through a factorial function line by line "
              "and see exactly how it works."),

        # Highlight + Line 1 explanation (play + play + wait(1.5) = 3.5s)
        (3.5, "Line one defines the function. It takes a single number n "
              "as input."),

        # Line 2 explanation (play + wait(1.5) = 2.5s)
        (2.5, "Line two is the base case check. If n is zero or one, "
              "we stop recursing."),

        # Line 3 explanation (play + wait(1.5) = 2.5s)
        (2.5, "Line three returns one for the base case — "
              "since zero factorial and one factorial both equal one."),

        # Line 4 explanation (play + wait(1.5) = 2.5s)
        (2.5, "Line four is the recursive case. We multiply n by "
              "the factorial of n minus one."),

        # FadeOut + code shrinks + trace title (1.5 + 1 + 1 = 3.5s)
        (3.5, "Now let's trace through an actual execution — "
              "factorial of five."),

        # Steps 1-3 (3 × 1.5s = 4.5s)
        (4.5, "Factorial of five expands to five times factorial of four, "
              "then five times four times factorial of three, and so on."),

        # Steps 4-6 (3 × 1.5s = 4.5s)
        (4.5, "We keep expanding until we reach factorial of one, "
              "which is just one. Now we can multiply everything together."),

        # Step 7 = 120 + wait(2) (1.5 + 2 = 3.5s)
        (3.5, "Five times four times three times two times one equals "
              "one hundred and twenty. That's factorial of five."),
    ]

    segments = []
    current_time = 0.0
    for duration, text in timeline:
        segments.append(NarrationSegment(
            start=round(current_time, 2),
            end=round(current_time + duration, 2),
            text=text,
        ))
        current_time += duration

    return segments


def explain_dijkstra_narration():
    """
    Narration timeline for ExplainDijkstra.

    Timing breakdown:
    - play(Write(title)) + wait() = 2s
    - play(FadeIn(code)) + wait() = 2s
    - play(code.animate.scale) = 1s
    - play(Create(all_nodes)) = 1s
    - play(Create(all_edges)) = 1s
    - wait() = 1s
    - play(Write(dist_label), Write(dist_display)) = 1s
    - play(highlight start) = 1s
    Dijkstra loop (6 nodes, variable edges):
      Node A: highlight(1) + edge AB highlight(1) + update B(1) + green edge(1)
              + edge AD highlight(1) + update D(1) + green edge(1) + mark(1) = 8s
      Node D: highlight(1) + edge DE highlight(1) + update E(1) + green edge(1) + mark(1) = 5s
      Node B: highlight(1) + edge BC highlight(1) + update C(1) + green edge(1)
              + edge BE highlight(1) + update E(1) + green edge(1) + mark(1) = 8s
      Node E: highlight(1) + edge EC highlight(1) + update C(1) + green edge(1)
              + edge EF highlight(1) + update F(1) + green edge(1) + mark(1) = 8s
      Node C: highlight(1) + edge CF highlight(1) + update F(1) + green edge(1) + mark(1) = 5s
      Node F: highlight(1) + mark(1) = 2s
    - play(Write(result)) + wait(2) = 3s
    Total ≈ 49s
    """
    timeline = [
        # Title + code (play + wait + play + wait = 4s)
        (4.0, "Dijkstra's algorithm finds the shortest path between "
              "nodes in a graph. Let's see the code and watch it run."),

        # Code shrinks + graph nodes + edges appear (1 + 1 + 1 + 1 = 4s)
        (4.0, "Here's a graph with six nodes connected by weighted edges. "
              "The numbers on each edge represent the cost to travel "
              "that connection."),

        # Distance display + start highlight (1 + 1 = 2s)
        (2.0, "We start at node A with a distance of zero. "
              "All other distances start at infinity."),

        # Process node A (8s)
        (4.0, "We visit node A first. Checking its neighbors — "
              "node B is four away, and node D is only two away."),
        (4.0, "We update the distances for B and D and mark those "
              "edges as part of potential shortest paths."),

        # Process node D (5s)
        (5.0, "Node D has the smallest distance, so we visit it next. "
              "From D, we can reach E with a total distance of seven."),

        # Process node B (8s)
        (4.0, "Now we visit node B. From B, we can reach C with a "
              "distance of seven, and E with a distance of five."),
        (4.0, "Five is better than the seven we had for E, "
              "so we update it."),

        # Process node E (8s)
        (4.0, "Node E is next. From E, we can reach C with a distance "
              "of seven — same as before — and F with a distance of nine."),
        (4.0, "We update F's distance and continue."),

        # Process node C (5s)
        (5.0, "From node C, we can reach F with a distance of eight, "
              "which is better than nine. We update F."),

        # Process node F + result (2 + 3 = 5s)
        (2.0, "Node F has no unvisited neighbors, so we're done."),
        (3.0, "All shortest paths from A have been found. "
              "This is the power of Dijkstra's algorithm — it "
              "guarantees the optimal path to every node."),
    ]

    segments = []
    current_time = 0.0
    for duration, text in timeline:
        segments.append(NarrationSegment(
            start=round(current_time, 2),
            end=round(current_time + duration, 2),
            text=text,
        ))
        current_time += duration

    return segments


def tcp_handshake_narration():
    """
    Narration timeline for TCPHandshake.

    Timing breakdown:
    Intro:
    - play(Write(intro_title)) = 1s
    - play(FadeIn(intro_lines)) = 1s
    - wait(2) = 2s
    - play(Write(analogy)) = 1s
    - wait(2) = 2s
    - play(FadeOut × 3) = 1s
    - wait(0.3) = 0.3s
    Main scene:
    - play(Write(title)) = 1s
    - play(FadeIn(client), FadeIn(server)) = 1s
    - wait(0.5) = 0.5s
    - play(Create(client_line), Create(server_line)) = 1s
    Step 1: play(badge+arrow+text+box+explain) = 1s, wait(2) = 2s → 3s
    Step 2: play(badge+arrow+text+Transform) = 1s, wait(2) = 2s → 3s
    Step 3: play(badge+arrow+text+Transform) = 1s, wait(2) = 2s → 3s
    Finale:
    - play(FadeOut(all)) = 1s
    - wait(0.3) = 0.3s
    - play(Write(summary_title)) = 1s
    - play(FadeIn(summary_steps)) = 1s
    - wait(1) = 1s
    - play(Write(summary_footer)) = 1s
    - wait(3) = 3s
    Total ≈ 28.9s
    """
    timeline = [
        # Intro title appears (play = 1s)
        (1.0, "What is TCP?"),

        # Intro paragraphs appear + wait (play + wait(2) = 3s)
        (3.0, "TCP, or Transmission Control Protocol, is the set of rules "
              "computers follow to send data reliably over the internet. "
              "Before any data is sent, both sides must agree to connect."),

        # Analogy appears + wait (play + wait(2) = 3s)
        (3.0, 'Think of it like a phone call. You dial, '
              'they pick up, and you say hello. '
              'That three-step process is called the handshake.'),

        # Transition: fade out intro + wait + title + client/server + wait + timelines
        # (1 + 0.3 + 1 + 1 + 0.5 + 1 = 4.8s)
        (4.8, "Let's see how this works between your computer "
              "and a website server."),

        # Step 1: SYN (play + wait(2) = 3s)
        (3.0, "Step one. Your computer sends a SYN message — short for "
              "synchronize. It's saying: hey, can we connect?"),

        # Step 2: SYN-ACK (play + wait(2) = 3s)
        (3.0, "Step two. The server replies with a SYN-ACK. "
              "That means: sure, I'm ready too. It confirms the "
              "request and asks the client to confirm back."),

        # Step 3: ACK (play + wait(2) = 3s)
        (3.0, "Step three. Your computer sends an ACK — short for "
              "acknowledge. It's saying: got it, let's go!"),

        # Finale: fade out + summary title + steps + wait + footer + wait
        # (1 + 0.3 + 1 + 1 + 1 + 1 + 3 = 8.3s)
        (3.0, "And that's it — the connection is established."),
        (2.0, "To recap: SYN, SYN-ACK, ACK."),
        (3.3, "Three simple messages, and now the two computers "
              "can safely exchange data."),
    ]

    segments = []
    current_time = 0.0
    for duration, text in timeline:
        segments.append(NarrationSegment(
            start=round(current_time, 2),
            end=round(current_time + duration, 2),
            text=text,
        ))
        current_time += duration

    return segments


SCENE_NARRATIONS = {
    "gradient_descent": gradient_descent_narration,
    "binary_search": binary_search_narration,
    "recursion": recursion_narration,
    "explain_factorial": explain_factorial_narration,
    "explain_dijkstra": explain_dijkstra_narration,
    "tcp_handshake": tcp_handshake_narration,
}


def generate_script(scene_name: str, output_path: Path):
    if scene_name not in SCENE_NARRATIONS:
        available = ", ".join(SCENE_NARRATIONS.keys())
        raise ValueError(
            f"No narration found for '{scene_name}'. Available: {available}"
        )

    segments = SCENE_NARRATIONS[scene_name]()

    output = {
        "scene": scene_name,
        "total_duration": segments[-1].end if segments else 0,
        "segments": [
            {
                "start": seg.start,
                "end": seg.end,
                "duration": round(seg.end - seg.start, 2),
                "text": seg.text,
            }
            for seg in segments
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2))
    print(f"Generated narration script: {output_path}")
    print(f"Total duration: {output['total_duration']}s")
    print(f"Segments: {len(output['segments'])}")

    # Also print the full script for review
    print("\n--- FULL SCRIPT ---\n")
    for seg in output["segments"]:
        print(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] ({seg['duration']:.1f}s)")
        print(f"  {seg['text']}\n")

    return output


if __name__ == "__main__":
    scene = sys.argv[1] if len(sys.argv) > 1 else "gradient_descent"
    out = Path(f"scripts/output/{scene}_narration.json")
    generate_script(scene, out)
