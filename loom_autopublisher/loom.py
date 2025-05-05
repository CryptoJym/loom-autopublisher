"""Loom asset extraction utilities (Day 1).

Functions here fetch raw video, transcript JSON, and thumbnail given a public
Loom *share* URL.  All I/O uses httpx + asyncio so callers can await or gather
multiple recordings in parallel.
"""
from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, Optional

import httpx


_VIDEO_URL = "https://cdn.loom.com/sessions/transcoded/{id}/720.mp4"
_TRANSCRIPT_URL = "https://cdn.loom.com/sessions/transcripts/{id}.json"
_THUMB_URL = "https://cdn.loom.com/sessions/thumbnails/{id}-with-play.jpg"


_ID_RE = re.compile(r"loom\.com/(?:share|embed)/([a-f0-9]{32})")


class LoomError(RuntimeError):
    """Raised on invalid URL or network failure."""


def extract_id(share_url: str) -> str:
    """Return 32-char Loom recording ID from a share URL.

    >>> extract_id("https://www.loom.com/share/0123456789abcdef0123456789abcdef")
    '0123456789abcdef0123456789abcdef'
    """
    m = _ID_RE.search(share_url)
    if not m:
        raise LoomError("Invalid Loom share URL")
    return m.group(1)


async def _get(client: httpx.AsyncClient, url: str) -> httpx.Response:
    """Helper ensuring 2xx status."""
    r = await client.get(url)
    r.raise_for_status()
    return r


async def fetch_assets(
    share_url: str,
    *,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """Download video bytes, transcript JSON, and thumbnail bytes.

    Returns a dict::
        {
            "id": str,
            "video": bytes,
            "transcript": list[dict],
            "thumbnail": bytes,
        }
    """
    recording_id = extract_id(share_url)

    async def _owned_client():
        # http2 gives a nice speed boost for Loom CDN
        return httpx.AsyncClient(http2=True, timeout=60)

    owned = False
    if client is None:
        client = await _owned_client()
        owned = True

    try:
        v_url = _VIDEO_URL.format(id=recording_id)
        t_url = _TRANSCRIPT_URL.format(id=recording_id)
        h_url = _THUMB_URL.format(id=recording_id)

        video_r, transcript_r, thumb_r = await asyncio.gather(
            _get(client, v_url),
            _get(client, t_url),
            _get(client, h_url),
        )

        return {
            "id": recording_id,
            "video": video_r.content,
            "transcript": transcript_r.json(),
            "thumbnail": thumb_r.content,
        }
    finally:
        if owned:
            await client.aclose()
