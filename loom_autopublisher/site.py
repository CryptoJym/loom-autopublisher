"""Site publishing helper (Day 4)."""

import os
import subprocess
from datetime import date
from pathlib import Path
from typing import Optional

__all__ = ["publish_walkthrough"]

async def publish_walkthrough(
    html_content: str,
    slug: str,
    title: str,
    yt_url: str,
    *,
    dry_run: bool = False,
) -> str:
    """
    Publish walkthrough page: create content/walkthroughs/{slug}.html with front matter,
    commit and push to remote site repo.
    Returns the URL of the new page.
    """
    # Front-matter
    front_matter = (
        f"---\n"
        f"title: {title}\n"
        f"date: {date.today().isoformat()}\n"
        f"yt: {yt_url}\n"
        f"---\n"
    )
    # File path
    filepath = Path("content/walkthroughs") / f"{slug}.html"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(front_matter + html_content, encoding="utf-8")

    if dry_run:
        return f"https://example.com/{slug}.html"

    # Git operations
    subprocess.run(["git", "add", str(filepath)], check=True)
    subprocess.run(["git", "commit", "-m", f"feat(walk): {slug}"], check=True)
    subprocess.run(["git", "push"], check=True)

    # Construct URL from SITE_URL env
    site_url = os.getenv("SITE_URL", "").rstrip("/")
    if not site_url:
        raise RuntimeError("SITE_URL must be set for real publish")
    return f"{site_url}/{slug}.html"
