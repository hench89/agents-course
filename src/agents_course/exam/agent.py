import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agents_course.exam.tools import TOOLS

load_dotenv()

#from langchain.globals import set_debug; set_debug(True)

def _get_llm_with_tools():
    deployment = os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT_NAME")
    llm = AzureChatOpenAI(deployment_name=deployment, temperature=0)
    return llm.bind_tools(TOOLS, parallel_tool_calls=False)


def _get_graph(llm: AzureChatOpenAI) -> CompiledStateGraph:

    class AgentState(TypedDict):
        messages: Annotated[list[AnyMessage], add_messages]

    def assistant(state: AgentState):
        new = llm.invoke(state["messages"])
        return {"messages": [new]}

    builder = StateGraph(AgentState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    return builder.compile()


def _get_agent():
    return _get_graph(_get_llm_with_tools())


template = """
    You are a general AI assistant.
    I will ask you a question.
    Report your thoughts, and finish your answer with the following template:
    FINAL ANSWER: [YOUR FINAL ANSWER].

    YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.
    If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.
    If the question is about a number, you should return the number as is, without any additional text.
    If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.
    If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.
    Use only the tools provided to you - do not use any other tools.

    {% if attachment %}
    Additional context is provided in the attachment: {{ attachment }}
    {% endif %}

    The question is: {{ question }}
"""

PROMPT_TEMPLATE = PROMPT_TEMPLATE = PromptTemplate(
    template=template,
    input_variables=["question", "attachment"],
    template_format="jinja2"
)


def ask_agent_a_question(question: str, attachment: str = None) -> str:
    app = _get_agent()
    prompt = PROMPT_TEMPLATE.format(question=question, attachment=attachment)
    response = app.invoke({"messages": [HumanMessage(content=prompt)]})
    response_text = response["messages"][-1]
    return response_text.content
