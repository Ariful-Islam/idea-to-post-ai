"""Ollama client wrapper with JSON-safe generation and one retry."""
import json
import re
from typing import Optional

import ollama

from app.config import settings

_client = ollama.AsyncClient(host=settings.OLLAMA_HOST)

SYSTEM_PROMPT = (
    "You are a social media copywriter. Given a rough idea, produce a single "
    "ready-to-publish post. Return ONLY a JSON object (no markdown fences, no "
    "commentary) with exactly these keys:\n"
    '  "hook": one punchy sentence that grabs attention,\n'
    '  "body": 1-2 short sentences expanding the idea,\n'
    '  "hashtags": array of 3-5 relevant hashtags WITHOUT the # symbol,\n'
    '  "cta": a short call-to-action string (may be empty string).\n'
    "Do not include any text outside the JSON object."
)

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(text: str) -> Optional[dict]:
    """Best-effort extraction of a JSON object from model output."""
    text = text.strip()
    # Strip common code fence wrappers
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = _JSON_RE.search(text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None


def _normalize(data: dict) -> dict:
    """Coerce model output into the expected shape."""
    hashtags = data.get("hashtags", [])
    if isinstance(hashtags, str):
        hashtags = [h.strip().lstrip("#") for h in hashtags.split(",") if h.strip()]
    elif isinstance(hashtags, list):
        hashtags = [str(h).strip().lstrip("#") for h in hashtags if str(h).strip()]
    else:
        hashtags = []

    return {
        "hook": str(data.get("hook", "")).strip(),
        "body": str(data.get("body", "")).strip(),
        "hashtags": hashtags,
        "cta": str(data.get("cta", "")).strip(),
    }


async def generate_post(idea: str) -> dict:
    """Call Ollama and return a normalized post dict."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Idea: {idea}"},
    ]

    for attempt in range(2):
        response = await _client.chat(model=settings.OLLAMA_MODEL, messages=messages)
        content = response["message"]["content"]

        parsed = _extract_json(content)
        if parsed and isinstance(parsed, dict):
            return _normalize(parsed)

        # Retry with a stronger nudge
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Idea: {idea}"},
            {
                "role": "assistant",
                "content": content,
            },
            {
                "role": "user",
                "content": "That was not valid JSON. Return ONLY a JSON object with keys hook, body, hashtags, cta.",
            },
        ]

    # Fallback: return a safe, minimal object so the UI never breaks
    return {
        "hook": idea.strip()[:120],
        "body": "Generation failed to return valid JSON. Try a shorter or clearer idea.",
        "hashtags": [],
        "cta": "",
    }