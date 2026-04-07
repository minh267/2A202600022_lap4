from __future__ import annotations

from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from tools import calculate_budget, search_flights, search_hotels

load_dotenv()

with open("system_prompt.txt", "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


TOOLS = [search_flights, search_hotels, calculate_budget]
LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0)
LLM_WITH_TOOLS = LLM.bind_tools(TOOLS)


def agent_node(state: AgentState) -> AgentState:
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = LLM_WITH_TOOLS.invoke(messages)

    if getattr(response, "tool_calls", None):
        for tool_call in response.tool_calls:
            print(f"Gọi tool: {tool_call['name']}({tool_call['args']})")
    else:
        print("Trả lời trực tiếp")

    return {"messages": [response]}


builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(TOOLS))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")
graph = builder.compile()


def run_chat() -> None:
    print("=" * 60)
    print("TravelBuddy — Trợ lý Du lịch Thông minh")
    print("Gõ 'quit' để thoát")
    print("=" * 60)

    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in {"quit", "exit", "q"}:
            break
        if not user_input:
            continue

        print("\nTravelBuddy đang suy nghĩ...")
        result = graph.invoke({"messages": [('human', user_input)]})
        final_message = result["messages"][-1]
        print(f"\nTravelBuddy: {final_message.content}")


if __name__ == "__main__":
    run_chat()
