"""Supabase client for updating video_requests status via REST API."""

import logging
from typing import Optional

import httpx

from config import settings

import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def update_request_status(
    request_id: str,
    status: str,
    video_url: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    """Update a video_requests row in Supabase via PostgREST."""
    # if not settings.supabase_url or not settings.supabase_service_role_key:
    #     logger.warning("[supabase] SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set — skipping")
    #     return

    load_dotenv()
    url = f"{settings.supabase_url}/rest/v1/video_requests?id=eq.{request_id}"
    headers = {
        "apikey": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_ROLE_KEY')}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    data: dict = {"status": status}
    if video_url is not None:
        data["video_url"] = video_url
    if error is not None:
        data["error"] = error

    try:
        resp = httpx.patch(url, json=data, headers=headers, timeout=10)
        resp.raise_for_status()
        logger.info("[supabase] Updated request %s → %s", request_id, status)
    except Exception as exc:
        logger.error("[supabase] Failed to update request %s: %s", request_id, exc)
