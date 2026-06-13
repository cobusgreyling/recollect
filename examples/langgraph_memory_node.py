"""
LangGraph pattern: memory write-back after the agent node.

pip install -e ".[langchain]" langgraph langchain-openai
"""

from __future__ import annotations

import os
from typing import TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from recollect import Memory, RecollectConfig


class State(TypedDict):
    user_id: str
    messages: list
    memories: str


def retrieve_memory(state: State) -> State:
    memory = Memory(RecollectConfig.local_dev())
    last = state["messages"][-1].content
    hits = memory.search(str(last), filters={"user_id": state["user_id"]}, top_k=5)
    lines = "\n".join(f"- {h['memory']}" for h in hits["results"])
    memory.close()
    return {**state, "memories": lines or "- none"}


def agent_node(state: State) -> State:
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"])
    prompt = f"Memories:\n{state['memories']}\n\nUser: {state['messages'][-1].content}"
    reply = llm.invoke(prompt).content
    return {**state, "messages": state["messages"] + [AIMessage(content=reply)]}


def persist_memory(state: State) -> State:
    memory = Memory(RecollectConfig.local_dev())
    user = state["messages"][-2].content
    assistant = state["messages"][-1].content
    memory.add(
        [{"role": "user", "content": str(user)}, {"role": "assistant", "content": str(assistant)}],
        user_id=state["user_id"],
        infer=False,
    )
    memory.close()
    return state


def build_graph():
    g = StateGraph(State)
    g.add_node("retrieve", retrieve_memory)
    g.add_node("agent", agent_node)
    g.add_node("persist", persist_memory)
    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "agent")
    g.add_edge("agent", "persist")
    g.add_edge("persist", END)
    return g.compile()


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY")
    app = build_graph()
    out = app.invoke(
        {
            "user_id": "lg1",
            "messages": [HumanMessage(content="Remember I deploy on Cloud Run")],
            "memories": "",
        }
    )
    print(out["messages"][-1].content)
