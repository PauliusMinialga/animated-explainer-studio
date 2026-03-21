# Animated Explainer Studio — Server

Generate Manim animations + narration scripts from any code snippet or concept.

## Architecture

```
POST /generate  ←  user prompt
     ↓
  Mistral (mistral-small-latest)
     ↓
  manim_script  +  TTSScript(intro, info, outro)
     ↓
  Manim render → animation.mp4
     ↓
  Response: { animation_url, tts_script }
```

Bote's pipeline consumes `tts_script` separately to generate TTS audio + avatar video.
Paul's frontend handles pre-cached concept videos via Supabase.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/generate` | Start generation job (returns `job_id`) |
| `GET` | `/jobs/{id}` | Poll job status, get `animation_url` + `tts_script` |
| `GET` | `/health` | Health check |
| `GET` | `/files/{job_id}/animation.mp4` | Serve rendered animation |

## Setup

```bash
cd server
chmod +x setup_env.sh && ./setup_env.sh
cp .env.template .env   # add MISTRAL_API_KEY
```

## Run

```bash
manim-env/bin/python -m uvicorn main:app --port 8000
```

## Project Structure

```
server/
├── main.py              # FastAPI app, CORS, /files mount
├── config.py            # MISTRAL_API_KEY
├── models.py            # GenerateRequest, JobResponse, TTSScriptResponse
├── database.py          # OUTPUT_DIR + job_dir()
├── requirements.txt
├── setup_env.sh
├── .env.template
├── pipeline/
│   ├── scripts.py       # Mistral → manim_script + TTSScript(intro/info/outro)
│   ├── manim_render.py  # Async Manim subprocess
│   └── enrich.py        # URL/GitHub enrichment
└── routers/
    ├── generate.py      # POST /generate, GET /jobs/{id}
    └── health.py        # GET /health
```

## Response Format

```json
{
  "job_id": "uuid",
  "status": "done",
  "animation_url": "/files/{job_id}/animation.mp4",
  "tts_script": {
    "intro": "Hey! Let's explore how Fibonacci works...",
    "info": "The code shows a recursive function that...",
    "outro": "Recursion breaks problems into smaller parts."
  }
}
```

## API Keys Required

| Key | Source | Used for |
|-----|--------|----------|
| `MISTRAL_API_KEY` | console.mistral.ai (free tier) | Script generation |

