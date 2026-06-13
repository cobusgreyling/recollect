from __future__ import annotations

import json
import re
from typing import Any

from recollect.config import LLMConfig

EXTRACTION_SYSTEM = """You extract durable facts from conversations for long-term agent memory.
Return JSON only: {"facts": ["fact one", "fact two"]}.
Rules:
- ADD-only: emit new atomic facts; never rewrite or delete prior knowledge in this response.
- Prefer stable preferences, identity, constraints, and confirmed outcomes.
- Skip greetings, filler, and ephemeral chit-chat.
- Each fact must stand alone (one sentence, third person where possible).
- Include agent-confirmed actions as facts when the user did not supply them explicitly.
"""

ENTITY_PATTERN = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b")


class FactExtractor:
    def __init__(self, config: LLMConfig) -> None:
        from openai import OpenAI

        self.config = config
        self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def extract(self, messages: list[dict[str, str]]) -> list[str]:
        if not messages:
            return []
        payload = json.dumps(messages, ensure_ascii=False)
        response = self._client.chat.completions.create(
            model=self.config.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM},
                {"role": "user", "content": f"Conversation JSON:\n{payload}"},
            ],
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        facts = data.get("facts", [])
        return [str(f).strip() for f in facts if str(f).strip()]


def extract_entities_heuristic(text: str) -> list[str]:
    found = ENTITY_PATTERN.findall(text)
    seen: set[str] = set()
    out: list[str] = []
    for item in found:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def parse_messages(
    data: str | list[dict[str, Any]],
) -> list[dict[str, str]]:
    if isinstance(data, str):
        text = data.strip()
        if not text:
            return []
        return [{"role": "user", "content": text}]
    out: list[dict[str, str]] = []
    for item in data:
        role = str(item.get("role", "user"))
        content = str(item.get("content", "")).strip()
        if content:
            out.append({"role": role, "content": content})
    return out