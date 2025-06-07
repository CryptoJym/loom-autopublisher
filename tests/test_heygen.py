import pytest

from loom_autopublisher.heygen import generate_intro


@pytest.mark.asyncio
async def test_generate_intro_dry_run(monkeypatch):
    # Ensure no live token so we exercise dry-run branch automatically.
    monkeypatch.delenv("HEYGEN_API_KEY", raising=False)

    intro_bytes = await generate_intro(
        script="Hello world! This is a sample intro.",
        dry_run=True,
    )

    assert isinstance(intro_bytes, bytes)
    # Stub returns deterministic 256-byte payload
    assert len(intro_bytes) == 256


@pytest.mark.asyncio
async def test_generate_intro_no_token(monkeypatch):
    """When no token is present we implicitly fall back to dry-run mode."""
    monkeypatch.delenv("HEYGEN_API_KEY", raising=False)

    intro_bytes = await generate_intro(script="Quick intro without token")
    assert len(intro_bytes) == 256
