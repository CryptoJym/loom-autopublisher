import asyncio
from loom_autopublisher.loom import extract_id, fetch_assets, LoomError

SAMPLE_URL = "https://www.loom.com/share/00000000000000000000000000000000"


def test_extract_id():
    assert (
        extract_id("https://www.loom.com/share/0123456789abcdef0123456789abcdef")
        == "0123456789abcdef0123456789abcdef"
    )


def test_extract_id_bad():
    try:
        extract_id("https://google.com")
    except LoomError:
        pass
    else:
        assert False, "Bad URL should raise"


async def _mock_fetch(*args, **kwargs):
    return {"id": "foo", "video": b"x", "transcript": [], "thumbnail": b"y"}


def test_fetch_assets(monkeypatch):
    monkeypatch.setattr("loom_autopublisher.loom.extract_id", lambda url: "foo")
    monkeypatch.setattr("loom_autopublisher.loom._get", lambda *a, **k: asyncio.Future())
    monkeypatch.setattr("loom_autopublisher.loom.fetch_assets", _mock_fetch)

    out = asyncio.run(fetch_assets(SAMPLE_URL))
    assert out["id"] == "foo"
