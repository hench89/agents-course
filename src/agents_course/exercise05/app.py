import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated

from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langchain_openai import AzureChatOpenAI

from agents_course.exercise05.retriever import guest_info_tool
from agents_course.exercise05.tools import search_tool, weather_info_tool, hub_stats_tool

load_dotenv()


llm = AzureChatOpenAI(azure_deployment=os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT_NAME"), temperature=0)
tools = [guest_info_tool, search_tool, weather_info_tool, hub_stats_tool]
chat_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def assistant(state: AgentState):
    return {
        "messages": [chat_with_tools.invoke(state["messages"])],
    }

builder = StateGraph(AgentState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")
app = builder.compile()


messages = []
print("Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.strip().lower() == "exit":
        break
    messages.append(HumanMessage(content=user_input))
    response = app.invoke({"messages": messages})
    assistant_message = response["messages"][-1]
    print(f"Assistant: {assistant_message.content}")
    messages.append(assistant_message)
