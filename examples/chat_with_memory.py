"""Minimal chat loop that injects retrieved memories into the system prompt."""

from __future__ import annotations

import os

from openai import OpenAI

from recollect import Memory, RecollectConfig
from recollect.config import EmbedderConfig, LLMConfig


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Set OPENAI_API_KEY to run this example.")

    memory = Memory(
        RecollectConfig(
            llm=LLMConfig(api_key=api_key),
            embedder=EmbedderConfig(provider="openai", api_key=api_key),
        )
    )
    client = OpenAI(api_key=api_key)
    user_id = "demo_user"

    print("Chat with memory (type 'exit')")
    while True:
        message = input("You: ").strip()
        if message.lower() == "exit":
            break

        retrieved = memory.search(message, filters={"user_id": user_id}, top_k=5)
        memory_lines = "\n".join(f"- {r['memory']}" for r in retrieved["results"])
        system = (
            "You are a helpful assistant. Use retrieved user memories when relevant.\n"
            f"User memories:\n{memory_lines or '- (none yet)'}"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message},
            ],
        )
        answer = response.choices[0].message.content or ""
        print(f"AI: {answer}")

        memory.add(
            [
                {"role": "user", "content": message},
                {"role": "assistant", "content": answer},
            ],
            user_id=user_id,
        )


if __name__ == "__main__":
    main()