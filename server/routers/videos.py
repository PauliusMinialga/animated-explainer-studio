from fastapi import APIRouter
from models import CachedVideo
from catalog import CATALOG, CATALOG_BY_SLUG, CatalogEntry
from database import get_cached_video_url

router = APIRouter(prefix="/videos", tags=["videos"])


def _entry_to_model(entry: CatalogEntry, video_url: str | None = None) -> CachedVideo:
    return CachedVideo(
        slug=entry.slug,
        title=entry.title,
        description=entry.description,
        category=entry.category,
        tags=entry.tags,
        video_url=video_url,
        duration_seconds=entry.duration_seconds,
        has_script=entry.has_script,
    )


@router.get("", response_model=list[CachedVideo])
async def list_videos():
    """Return the full concept catalog with video URLs where available."""
    result = []
    for entry in CATALOG:
        video_url = await get_cached_video_url(entry.slug)
        result.append(_entry_to_model(entry, video_url))
    return result


@router.get("/{slug}", response_model=CachedVideo)
async def get_video(slug: str):
    entry = CATALOG_BY_SLUG.get(slug)
    if not entry:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"No concept with slug '{slug}'")
    video_url = await get_cached_video_url(slug)
    return _entry_to_model(entry, video_url)
