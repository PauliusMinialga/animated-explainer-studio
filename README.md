# 🎬 Animated Explainer Studio

AI-powered visual explanations for **code snippets**, **programming concepts**, and **GitHub repositories**.

Instead of forcing users to reconstruct a system from raw code, Animated Explainer Studio turns technical content into a guided visual walkthrough.

---

## 🎥 Demo

Here is an example of a generated explanation (Bresenham algorithm):

https://github.com/user-attachments/assets/049fd686-d5a1-4b41-accb-44a3d3328bec

This demonstrates how the system explains an algorithm step by step, using animation and narration.

⸻

🚀 Why we built this

Understanding code is still one of the slowest parts of software development.

When you open a new function or a new repository, you usually have to:
	•	read several files manually
	•	infer structure from naming and imports
	•	rebuild the system mentally
	•	guess how components interact

At the same time, AI is making code generation faster and more accessible.

👉 The challenge is shifting.

It’s no longer just about writing code — it’s about understanding architecture, systems, and design decisions.

Animated Explainer Studio is designed for that shift.

⸻

💡 What problem it solves

This project helps reduce the time it takes to understand:
	•	a function
	•	a code snippet
	•	a concept (arrays, pointers, memory, algorithms…)
	•	a complete GitHub repository architecture

Instead of a static explanation, users get a visual, narrated, step-by-step walkthrough.

⸻

🎯 Target audience
	•	developers onboarding into a new codebase
	•	students learning programming concepts
	•	engineers reviewing unfamiliar logic
	•	hackathon teams and interview candidates
	•	anyone who wants a fast mental model of code

⸻

🧠 Product modes

✏️ Prompt Mode

Explain:
	•	code snippets
	•	functions
	•	algorithms
	•	programming concepts

The system automatically routes the request:
	•	Code explanation → structured visual scenes (React Flow)
	•	Concept / algorithm explanation → animation-based visualization (Manim)

Examples:
	•	“Explain this function”
	•	“Explain binary search”
	•	“Explain malloc and free”
	•	“Explain arrays”

If a GitHub repo is provided, it is used as context, not as the main subject.

⸻

🏗️ Repo Mode (🔥 core feature)

Provide a GitHub repository, and the system:
	•	extracts main components
	•	identifies responsibilities
	•	maps interactions and data flow
	•	builds a structured explanation

Instead of reading folders, you see the architecture.

👉 This is the strongest “wow” part of the project.

⸻

⚙️ How it works

Prompt Mode
	1.	Analyze prompt / snippet
	2.	Classify: code vs concept
	3.	Generate structured explanation
	4.	Render scenes or animation
	5.	Generate narration + video
	6.	Output playable/downloadable result

⸻

Repo Mode (AI pipeline)
	1.	Ingest repository
	2.	Extract architecture (components, flows, responsibilities)
	3.	Build structured representation
	4.	Convert into a teaching storyboard
	5.	Render scene-by-scene explanation (React Flow)
	6.	Generate narration + video

👉 The key idea: we don’t explain files — we explain systems

⸻

🧩 Design approach

We don’t treat code as raw text.

We transform it into:
	•	structured representations
	•	logical components
	•	visual flows
	•	progressive explanations

This allows:
	•	better comprehension
	•	clearer mental models
	•	faster onboarding

⸻

🛠️ Tech stack

Frontend
	•	Vite
	•	React
	•	TypeScript
	•	Tailwind CSS
	•	React Flow

Used for:
	•	scene rendering
	•	visual architecture mapping
	•	interactive explanations

⸻

Backend
	•	FastAPI
	•	Python
	•	Mistral (LLM)
	•	Manim (animation)
	•	Runware / fal.ai (video & avatar)
	•	ffmpeg (final composition)
	•	Supabase

Handles:
	•	prompt + repo analysis
	•	architecture extraction
	•	storyboard generation
	•	narration generation
	•	video assembly

⸻

🔍 Why React Flow

We moved away from generated animation scripts for repo explanations.

React Flow gives:
	•	stable layouts
	•	clean architecture visualization
	•	step-by-step focus
	•	deterministic rendering (critical for demo reliability)

⸻

🎬 Why Manim (selectively)

Manim is used only when motion is essential:
	•	algorithms (e.g. Bresenham)
	•	memory behavior
	•	arrays / pointers
	•	dynamic processes

To avoid instability:
👉 only one controlled animation flow per explanation

⸻

📁 Repository structure
```
.
├── client/      # frontend (React + React Flow)
├── server/      # backend (AI + pipelines + video)
├── supabase/    # storage / backend support
├── .env.template
├── package.json
└── requirements.txt
```

⸻

🚀 What makes this project interesting

This is not just AI summarizing code.

It is a pipeline that:
	1.	understands structure
	2.	converts it into a teaching sequence
	3.	renders it visually
	4.	narrates it as a guided experience

👉 The goal is not to read code faster
👉 The goal is to understand systems faster

⸻

🔮 Possibilities
	•	developer onboarding tools
	•	education platforms
	•	interview preparation
	•	documentation automation
	•	AI-assisted code review
	•	architecture visualization for teams

⸻

🎯 Demo tip

If you are reviewing this project:

👉 Try Repo Mode first

It best demonstrates the full vision.
