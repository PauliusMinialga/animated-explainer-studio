# Voiceover Pipeline: Manim Animation → Synced Narration

## Overview

This guide explains how to generate voiceover scripts that stay in sync with Manim animations. The key insight is that **Manim has deterministic timing**, so we can pre-calculate exactly when each visual event happens and write narration to match.

---

## How Manim Timing Works

| Manim Call | Default Duration |
|---|---|
| `self.play(...)` | 1 second |
| `self.play(..., run_time=N)` | N seconds |
| `self.wait()` | 1 second |
| `self.wait(N)` | N seconds |

So if your scene has `play → wait → play → play`, the total is 4 seconds, and you know exactly what's on screen at each second.

---

## Step-by-Step Process

### 1. Write the Manim animation first

Get the visuals right. Don't worry about narration yet.

### 2. Count the timing

Walk through your `construct()` method and add up durations:

```
self.play(Write(title))      # 0s - 1s
self.wait()                   # 1s - 2s
self.play(Create(axes))       # 2s - 3s
self.play(Create(graph))      # 3s - 4s
self.wait()                   # 4s - 5s
```

### 3. Write narration segments

For each time window, write what the narrator should say. The text length should roughly match the time available (~2-3 words per second for natural speech).

**Rules of thumb:**
- ~150 words per minute is natural narration speed
- That's ~2.5 words per second
- A 4-second window fits about 10 words comfortably
- Leave brief pauses between segments (don't fill every second)

### 4. Create the narration timeline

Use `scripts/generate_narration.py` to define segments:

```python
timeline = [
    (2.0, "Gradient descent is one of the most important optimization algorithms."),
    (1.0, "We'll start with a simple function."),
    (3.0, "Here's f of x equals x squared — a parabola."),
]
```

Each tuple is `(duration_in_seconds, narration_text)`.

### 5. Generate the JSON script

```bash
cd the_project
python scripts/generate_narration.py gradient_descent
```

This outputs `scripts/output/gradient_descent_narration.json` with timestamped segments.

### 6. Generate TTS audio

Feed the JSON to a TTS service. Options:
- **VEED API** — we have an API key in `.env`
- **ElevenLabs** — high quality voices
- **OpenAI TTS** — good quality, easy API
- **Google Cloud TTS** — free tier available

### 7. Combine video + audio

Either:
- Use VEED's API to merge
- Use `ffmpeg`: `ffmpeg -i video.mp4 -i narration.mp3 -c:v copy -c:a aac output.mp4`

---

## Adjusting Timing (When Narration Doesn't Fit)

If your narration is too long for a segment, you have two options:

**Option A: Shorten the narration** (preferred — keeps animation snappy)

**Option B: Slow down the animation** — add `run_time` or `self.wait()`:

```python
# Before: too fast for narration
self.play(Create(graph))  # only 1s

# After: gives narrator time to explain
self.play(Create(graph), run_time=2)  # now 2s
self.wait(1)  # extra 1s pause
```

---

## Pacing Tips for Good Voiceovers

1. **Front-load explanation**: Explain a concept BEFORE or AS the visual appears, not after
2. **Reduce narration over repetition**: If the animation loops (like gradient descent steps), explain fully on step 1-2, then use shorter commentary for later steps
3. **Use silence**: Not every second needs narration. Let complex visuals breathe
4. **Match energy to visuals**: Fast animations → concise narration. Slow builds → detailed explanation
5. **End with the takeaway**: Last segment should connect to the big picture

---

## LaTeX Gotcha

Manim uses LaTeX for `MathTex` and axis number labels. If LaTeX isn't installed:
- Use `Text("f(x) = x²")` instead of `MathTex("f(x) = x^2")`
- Set `axis_config={"include_numbers": False}` on `Axes`
- Use `Text()` objects for axis labels instead of string args to `get_axis_labels()`

To install LaTeX: `brew install --cask mactex-no-gui` (~800MB)

---

## File Structure

```
scripts/
├── generate_narration.py      # Narration timeline definitions + JSON generator
├── output/
│   └── gradient_descent_narration.json  # Generated timestamped script
└── VOICEOVER_GUIDE.md         # This file
```

## Adding Narration for a New Scene

1. Open `scripts/generate_narration.py`
2. Add a new function (e.g., `def binary_search_narration()`)
3. Count timing from your Manim scene's `construct()` method
4. Add the function to `SCENE_NARRATIONS` dict
5. Run: `python scripts/generate_narration.py binary_search`
