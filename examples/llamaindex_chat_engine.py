"""
LlamaIndex SimpleChatEngine with RecollectMemory (local, no API keys).

pip install -e . && pip install -e packages/llama-index-memory-recollect
pip install llama-index-llms-openai  # only if using a real LLM
"""

from __future__ import annotations

from llama_index.core import SimpleChatEngine
from llama_index.memory.recollect import RecollectMemory

from recollect.config import RecollectConfig


def main() -> None:
    config = RecollectConfig.local_dev()
    memory = RecollectMemory.from_config(context={"user_id": "mayank"}, config=config)

    # Swap in your LLM; this example focuses on memory wiring.
    try:
        from llama_index.llms.openai import OpenAI

        llm = OpenAI(model="gpt-4o-mini")
    except Exception:
        print("Install llama-index-llms-openai and set OPENAI_API_KEY for a live chat.")
        print("Memory adapter is configured:", memory.class_name())
        return

    engine = SimpleChatEngine.from_defaults(llm=llm, memory=memory)
    print(engine.chat("Hi, my name is Mayank and I build agent memory systems."))
    print(engine.chat("What do you remember about me?"))


if __name__ == "__main__":
    main()