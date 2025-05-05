"""Content generator that turns a Loom transcript into multi-channel copy.

The single public async helper `generate_content` returns a dict with keys:
    title, description, teaser, slug, walkthrough_html

Under the hood this calls OpenAI ChatCompletion with GPT-4o and instructs the
model to output **valid JSON only**.  Tests patch `openai.ChatCompletion.create`
so no network call is made.
"""
from __future__ import annotations

import asyncio
import json
import os
from difflib import get_close_matches
from pathlib import Path
from typing import Dict, Optional

import openai

__all__ = ["generate_content"]

_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

_SYSTEM_PROMPT = (
    "You are a content-marketing assistant. Given a video transcript, "
    "generate a short catchy title (<60 characters), a 1-sentence teaser "
    "(<110 characters), a YouTube description (<150 words), and a kebab-case "
    "slug. Then wrap the transcript into branded HTML that matches the CSS "
    "variables provided.  Output ONLY valid JSON with exactly the keys: "
    "title, description, teaser, slug, walkthrough_html."
)

_JSON_SCHEMA = (
    '{"title":"string","description":"string","teaser":"string","slug":"string","walkthrough_html":"string"}'
)


async def _arequest(messages):
    """Async thin wrapper because the SDK is sync-only."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: openai.ChatCompletion.create(
            model=_MODEL,
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        ),
    )


async def generate_content(
    transcript: str,
    *,
    brand_css_path: Optional[Path] = None,
) -> Dict[str, str]:
    """Generate content dict from transcript.

    `brand_css_path` should point to `/styles/variables.css` in the site repo.
    If missing, we still proceed but note so in the prompt.
    """
    if not transcript.strip():
        raise ValueError("Empty transcript")

    css_vars = "/* brand CSS not found */"
    if brand_css_path and brand_css_path.exists():
        css_vars = brand_css_path.read_text()[:2048]  # limit prompt size

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": f"BRAND_CSS:\n{css_vars}"},
        {"role": "user", "content": f"TRANSCRIPT:\n{transcript}"},
        {"role": "user", "content": f"Return JSON matching this schema:\n{_JSON_SCHEMA}"},
    ]

    rsp = await _arequest(messages)
    txt = rsp.choices[0].message.content  # type: ignore[attr-defined]
    try:
        parsed = json.loads(txt)
    except json.JSONDecodeError as e:
        # Attempt to recover by finding the closest braces block
        start = txt.find("{")
        end = txt.rfind("}")
        if start != -1 and end != -1:
            parsed = json.loads(txt[start : end + 1])
        else:
            raise RuntimeError("LLM returned non-JSON") from e

    # Basic sanity checks
    required = {
        "title": 60,
        "description": 150 * 8,  # ~150 words × avg 8 chars
        "teaser": 110,
        "slug": 100,
        "walkthrough_html": 1,
    }
    for key, limit in required.items():
        if key not in parsed:
            raise KeyError(f"Missing key {key} in LLM output")
        if key in ("walkthrough_html"):
            continue
        if len(parsed[key]) > limit:
            close = get_close_matches(key, parsed.keys())
            raise ValueError(f"{key} too long; got {len(parsed[key])} chars. keys: {close}")

    return parsed
