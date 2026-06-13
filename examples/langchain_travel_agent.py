"""
LangChain + Recollect travel-agent style loop (retrieve → answer → persist).

Requires: pip install -e ".[openai,langchain]" and OPENAI_API_KEY.
"""

from __future__ import annotations

import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from recollect import Memory, RecollectConfig
from recollect.integrations.langchain.tools import format_memories_for_prompt


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Set OPENAI_API_KEY")

    memory = Memory(RecollectConfig())
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
    user_id = "traveler_1"

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content="You are a travel agent. Use retrieved memories to personalize advice."
            ),
            MessagesPlaceholder(variable_name="context"),
            HumanMessage(content="{input}"),
        ]
    )
    chain = prompt | llm

    def turn(user_input: str) -> str:
        hits = memory.search(user_input, filters={"user_id": user_id}, top_k=5)
        context = [
            SystemMessage(content=f"Memories:\n{format_memories_for_prompt(hits) or '- none'}")
        ]
        reply = chain.invoke({"context": context, "input": user_input}).content
        memory.add(
            [{"role": "user", "content": user_input}, {"role": "assistant", "content": reply}],
            user_id=user_id,
        )
        return reply

    print(turn("I prefer boutique hotels and vegetarian food."))
    print(turn("Suggest a weekend in Lisbon."))


if __name__ == "__main__":
    main()