"""HeyGen avatar video generator (Day 5).

This helper wraps the HeyGen API to generate a short avatar intro video.
For CI we support *dry-run* mode where no network request is made and dummy
MP4 bytes are returned.  A future implementation can extend this stub to hit
HeyGen's `/videos/create` and `/videos/{id}` endpoints.
"""
from __future__ import annotations

import os
import random
import string
import time
from typing import Optional

import httpx

__all__ = ["generate_intro", "HeyGenError"]


class HeyGenError(RuntimeError):
    """Raised when HeyGen video generation fails."""


def _rand_bytes(size: int = 256) -> bytes:  # simple deterministic bytes for tests
    rnd = random.Random(42)  # fixed seed so snapshot tests stay stable
    return bytes(rnd.randrange(256) for _ in range(size))


async def generate_intro(
    script: str,
    *,
    voice: str = "jenny",
    model_id: Optional[str] = None,
    dry_run: bool = False,
    poll_interval: float = 2.5,
    timeout: float = 60.0,
) -> bytes:
    """Generate a ~15 second avatar intro MP4 from the given ``script``.

    Parameters
    ----------
    script:
        The short script to speak (HeyGen supports up to ~300 chars for intro).
    voice:
        HeyGen voice name.  Ignored in dry-run mode.
    model_id:
        Optional avatar model ID.  If *None* defaults to HeyGen's standard.
    dry_run:
        When *True* (default if ``HEYGEN_API_KEY`` env var is missing) we avoid
        external I/O and return dummy bytes immediately.
    poll_interval & timeout:
        Used by future real implementation to poll job status.
    """
    token = os.getenv("HEYGEN_API_KEY")
    if dry_run or not token:
        return _rand_bytes()

    # --- Stubbed network call until real integration ---
    raise HeyGenError("Live HeyGen calls not yet implemented. Use dry_run=True.")
