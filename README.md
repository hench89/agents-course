# Getting Started (notes from course material)

- Install and set up Ollama:
    - `brew install ollama`
    - `ollama pull qwen2:7b`
    - `ollama serve`

## Agents

- Agent: A system with agency—the ability to interact with its environment.
- An Agent leverages an AI model to achieve user-defined objectives by combining reasoning, planning, and executing actions (often via external tools).
- Agents consist of:
    1. The Brain / AI Model
    2. The Body (Capabilities and Tools)
- The most common AI model in Agents is an LLM (Large Language Model), which processes and generates text.
- Agents use AI models (typically LLMs) to:
    - Understand natural language and respond meaningfully
    - Reason, plan, and solve problems
    - Interact with their environment by gathering information, taking actions, and observing outcomes

## The ReAct Framework

The name "ReAct" is based on the concatenation of two words: “Reason” and “Act.” Agents following this architecture solve their tasks in as many steps as needed, with each step consisting of a Reasoning step followed by an Action step.


## Accessing huggingface inference providers

1. generate token on https://huggingface.co/settings/tokens
2. in .env file add HF_TOKEN=....
3. in python: `from dotenv import load_dotenv; load_dotenv()`

