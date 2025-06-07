"""YouTube upload helper (Day 3).

For CI we support *dry-run* mode that returns a fake URL so tests need no
Google credentials.  A future implementation can replace the stubbed section
with real calls to YouTube Data API v3.
"""
from __future__ import annotations

import os
import random
import string
from pathlib import Path
from typing import Optional

__all__ = ["upload_video", "YouTubeError"]


class YouTubeError(RuntimeError):
    """Raised when upload fails."""


def _rand_id() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=11))


def _ensure_bytes(data: str | bytes | Path) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, (str, Path)):
        return Path(data).read_bytes()
    raise TypeError(" unsupported type for bytes")


async def upload_video(
    video: str | bytes | Path,
    *,
    title: str,
    description: str,
    thumbnail: Optional[str | bytes | Path] = None,
    dry_run: bool = False,
) -> str:
    """Upload an MP4 to YouTube and optionally set a custom thumbnail.

    In test/CI environments pass ``dry_run=True`` (default when
    ``YOUTUBE_API_KEY`` env var is missing).  In that mode we do no network
    I/O and immediately return a fake watch URL.
    """
    token = os.getenv("YOUTUBE_API_KEY")
    if dry_run or not token:
        vid = _rand_id()
        return f"https://youtube.com/watch?v={vid}"

    # Stub implementation for non-dry_run mode (Day 3)
    vid = _rand_id()
    if thumbnail is not None:
        # validate thumbnail bytes
        _ensure_bytes(thumbnail)
    return f"https://youtube.com/watch?v={vid}"
