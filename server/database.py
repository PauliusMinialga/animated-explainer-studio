from functools import lru_cache
from pathlib import Path

# Local output directory — generated videos are served directly from FastAPI
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def job_dir(job_id: str) -> Path:
    d = OUTPUT_DIR / job_id
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── Supabase (optional — not used in MVP, kept for future) ──────────────────

def get_supabase():
    from config import settings
    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set")
    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_key)


async def get_cached_video_url(slug: str) -> str | None:
    """Fetch the video_url for a cached video from Supabase (optional)."""
    try:
        client = get_supabase()
        result = (
            client.table("cached_videos")
            .select("video_url")
            .eq("slug", slug)
            .single()
            .execute()
        )
        return result.data.get("video_url") if result.data else None
    except Exception:
        return None
