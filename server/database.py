from functools import lru_cache
from supabase import create_client, Client
from config import settings


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(settings.supabase_url, settings.supabase_key)


async def get_cached_video_url(slug: str) -> str | None:
    """Fetch the video_url for a cached video from Supabase."""
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


async def upsert_cached_video(slug: str, video_url: str) -> None:
    """Store or update a cached video URL in Supabase."""
    client = get_supabase()
    client.table("cached_videos").upsert(
        {"slug": slug, "video_url": video_url}
    ).execute()


async def upload_video(local_path: str, remote_name: str) -> str:
    """Upload a video file to Supabase Storage and return its public URL."""
    client = get_supabase()
    with open(local_path, "rb") as f:
        client.storage.from_(settings.video_bucket).upload(
            remote_name,
            f,
            {"content-type": "video/mp4", "upsert": "true"},
        )
    return client.storage.from_(settings.video_bucket).get_public_url(remote_name)
