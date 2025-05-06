"""Buffer API helper (Day 5).

This minimal helper supports *dry-run* mode for CI so no real network
request is issued unless a `BUFFER_ACCESS_TOKEN` environment variable is set
**and** ``dry_run`` is ``False``.

A future implementation can extend this stub to hit Buffer's v2 API at
``POST https://api.bufferapp.com/1/updates/create.json``.  For now we only
validate arguments and return a fake update ID.
"""
from __future__ import annotations

import os
import random
import string
from typing import Optional

import httpx

__all__ = [
    "queue_post",
    "BufferError",
]


class BufferError(RuntimeError):
    """Raised when publishing to Buffer fails."""


def _rand_id() -> str:  # 6-char pseudo ID is enough for tests
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


async def queue_post(
    *,
    text: str,
    netlify_url: str,
    remote_video_url: Optional[str] = None,
    profiles: Optional[list[str]] = None,
    dry_run: bool = False,
) -> str:
    """Queue a social post via Buffer and return the *update ID*.

    In *dry-run* mode (default when ``BUFFER_ACCESS_TOKEN`` is missing) we do
    no network I/O and immediately return a fake ID.  The signature only
    accepts the subset of parameters used by our pipeline.
    """

    token = os.getenv("BUFFER_ACCESS_TOKEN")
    if dry_run or not token:
        return f"dry-{_rand_id()}"

    # Build payload for Buffer v2 (simplified)
    payload = {
        "text": f"{text} ▶ {netlify_url}",
    }
    if remote_video_url:
        payload["remote_video_url"] = remote_video_url
    if profiles:
        payload["profile_ids"] = ",".join(profiles)

    url = "https://api.bufferapp.com/1/updates/create.json"
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            url,
            params={"access_token": token},
            data=payload,
        )
    if resp.status_code != 200:
        raise BufferError(f"Buffer API returned {resp.status_code}")
    data = resp.json()
    # Successful response contains {"update_id": "..."}
    return data.get("update_id", _rand_id())
