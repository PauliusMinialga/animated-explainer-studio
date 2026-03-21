"""Supabase client for updating video_requests status."""

import logging
from typing import Optional

from supabase import create_client, Client

from config import settings

logger = logging.getLogger(__name__)

_client: Optional[Client] = None


def get_client() -> Optional[Client]:
    global _client
    if _client is not None:
        return _client
    logger.info("[supabase] SUPABASE_URL=%r, SERVICE_KEY=%s",
                settings.supabase_url,
                "set" if settings.supabase_service_role_key else "empty")
    if not settings.supabase_url or not settings.supabase_service_role_key:
        logger.warning("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set — status updates disabled")
        return None
    _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _client


def update_request_status(
    request_id: str,
    status: str,
    video_url: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    """Update a video_requests row in Supabase. Silently skips if client is unavailable."""
    client = get_client()
    if client is None:
        return
    try:
        data: dict = {"status": status}
        if video_url is not None:
            data["video_url"] = video_url
        if error is not None:
            data["error"] = error
        client.table("video_requests").update(data).eq("id", request_id).execute()
        logger.info("[supabase] Updated request %s → %s", request_id, status)
    except Exception as exc:
        logger.error("[supabase] Failed to update request %s: %s", request_id, exc)
