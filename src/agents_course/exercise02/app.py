"""
This exercise is about creating a code agent that can perform web searches and visit webpages.
The agent will be able to search for information on the web and visit webpages to gather information.
"""

from smolagents import CodeAgent, LiteLLMModel
import yaml
from agents_course.exercise02 import tools


final_answer = tools.FinalAnswerTool()
web_search = tools.DuckDuckGoSearchTool()
visit_webpage = tools.VisitWebpageTool()
model = LiteLLMModel(model_id="ollama_chat/qwen2:7b", api_base="http://127.0.0.1:11434", num_ctx=8192)

with open("./src/agents_course/exercise02/prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

agent = CodeAgent(
    model=model,
    tools=[visit_webpage, web_search, final_answer],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates # Pass system prompt to CodeAgent
)

while True:
    user_input = input("User: ")
    if user_input.lower() == "exit":
        break
    response = agent(user_input)
    print(f"Agent: {response}")

