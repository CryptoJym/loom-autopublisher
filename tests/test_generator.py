import asyncio
import json
from pathlib import Path

import pytest

from loom_autopublisher import generator as gen


class DummyRsp:
    class Choice:
        def __init__(self, content):
            self.message = type("Msg", (), {"content": content})

    def __init__(self, content):
        self.choices = [self.Choice(content)]


@pytest.mark.asyncio
async def test_generate_content(monkeypatch, tmp_path: Path):
    dummy_json = json.dumps(
        {
            "title": "Cool Loom Walkthrough",
            "description": "This is a short description under 150 words.",
            "teaser": "Quick tour of the new feature!",
            "slug": "cool-loom-walkthrough",
            "walkthrough_html": "<div>hello world</div>",
        }
    )

    monkeypatch.setattr(
        "openai.ChatCompletion.create", lambda *a, **k: DummyRsp(dummy_json)
    )

    transcript = "Hello world. This is a test transcript."
    css_file = tmp_path / "variables.css"
    css_file.write_text(":root { --brand: #123; }")

    out = await gen.generate_content(transcript, brand_css_path=css_file)
    assert out["slug"].startswith("cool-")
    assert "<div" in out["walkthrough_html"]
