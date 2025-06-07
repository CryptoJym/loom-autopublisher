import asyncio
import pytest
from loom_autopublisher.youtube import upload_video


@pytest.mark.asyncio
async def test_dry_run():
    url = await upload_video(b"fake mp4 bytes", title="t", description="d", dry_run=True)
    assert url.startswith("https://youtube.com/watch?v=")
