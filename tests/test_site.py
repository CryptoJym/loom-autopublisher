import os
import pytest
from pathlib import Path

from loom_autopublisher.site import publish_walkthrough


@pytest.mark.asyncio
async def test_publish_walkthrough_dry_run(tmp_path, monkeypatch):
    # Change working directory to tmp
    monkeypatch.chdir(tmp_path)
    html = "<p>content</p>"
    url = await publish_walkthrough(
        html_content=html,
        slug="test-slug",
        title="Test Title",
        yt_url="http://yt",
        dry_run=True,
    )
    assert url == "https://example.com/test-slug.html"
    # Check file created with front matter and content
    fpath = tmp_path / "content" / "walkthroughs" / "test-slug.html"
    assert fpath.exists()
    text = fpath.read_text(encoding="utf-8")
    assert "title: Test Title" in text
    assert html in text


@pytest.mark.asyncio
async def test_publish_walkthrough_real(tmp_path, monkeypatch):
    # Change working directory to tmp
    monkeypatch.chdir(tmp_path)
    html = "<p>hi</p>"
    # Prepare fake subprocess calls
    calls = []
    def fake_run(cmd, check):
        calls.append(cmd)
    # Set SITE_URL
    monkeypatch.setenv("SITE_URL", "https://mysite.com")
    # Patch subprocess.run in site module
    monkeypatch.setattr("loom_autopublisher.site.subprocess.run", fake_run)

    url = await publish_walkthrough(
        html_content=html,
        slug="demo",
        title="D",
        yt_url="http://yt",
        dry_run=False,
    )
    # Validate git commands
    expected_file = str(tmp_path / "content" / "walkthroughs" / "demo.html")
    assert calls[0] == ["git", "add", expected_file]
    assert calls[1] == ["git", "commit", "-m", "feat(walk): demo"]
    assert calls[2] == ["git", "push"]
    # Validate returned URL
    assert url == "https://mysite.com/demo.html"
