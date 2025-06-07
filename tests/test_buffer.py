import pytest

from loom_autopublisher.buffer import queue_post


@pytest.mark.asyncio
async def test_queue_post_dry_run(monkeypatch):
    # Ensure no live token
    monkeypatch.delenv("BUFFER_ACCESS_TOKEN", raising=False)
    update_id = await queue_post(text="hello", netlify_url="https://example.com")
    assert update_id.startswith("dry-")


class _FakeResp:
    def __init__(self, status_code=200):
        self.status_code = status_code

    def json(self):
        return {"update_id": "u12345"}


class _FakeClient:
    def __init__(self, *a, **kw):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *a, **kw):
        return _FakeResp()


@pytest.mark.asyncio
async def test_queue_post_real(monkeypatch):
    monkeypatch.setenv("BUFFER_ACCESS_TOKEN", "tok")
    # Replace AsyncClient with fake
    monkeypatch.setattr("loom_autopublisher.buffer.httpx.AsyncClient", _FakeClient)

    update_id = await queue_post(
        text="hi",
        netlify_url="https://n",
        remote_video_url="https://v",
        profiles=["p1", "p2"],
        dry_run=False,
    )
    assert update_id == "u12345"
