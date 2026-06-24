from __future__ import annotations

import json
import os
import time
from typing import Any

import requests


DEFAULT_MODEL = "agnes-2.0-flash"
DEFAULT_BASE_URL = "https://apihub.agnes-ai.com/v1"


def model_metadata() -> dict:
    has_key = bool(_api_key())
    return {
        "model_provider": "agnes-ai" if has_key else "fallback",
        "model_name": _model_name() if has_key else "deterministic-template",
        "model_mode": "live" if has_key else "fallback",
    }


def complete_json(system_prompt: str, user_payload: dict[str, Any], timeout: int = 60) -> dict | None:
    api_key = _api_key()
    if not api_key:
        return None
    base_url = _base_url()
    model = _model_name()
    body = {
        "model": model,
        "temperature": 0.15,
        "max_tokens": 2200,
        "messages": [
            {"role": "system", "content": system_prompt + "\n只输出一个合法 JSON 对象，不要输出 Markdown 代码块。"},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
    }
    for attempt in range(2):
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={"authorization": f"Bearer {api_key}", "content-type": "application/json"},
                json=body,
                timeout=timeout,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            parsed = _parse_json_object(content)
            if parsed:
                return parsed
        except Exception:
            if attempt == 0:
                time.sleep(1)
                continue
    return None


def _api_key() -> str:
    return os.getenv("MODEL_API_KEY", "").strip()


def _base_url() -> str:
    return os.getenv("MODEL_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _model_name() -> str:
    return os.getenv("MODEL_NAME", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _parse_json_object(content: str) -> dict | None:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return None
    return None
