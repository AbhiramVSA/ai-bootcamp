# 01_basic_agent.py
# The simplest possible PydanticAI agent.
# Run: python 01_basic_agent.py

from settings import settings  # noqa: F401 — loads .env
from pydantic_ai import Agent

agent = Agent('openai:gpt-5-mini', system_prompt='You are a helpful assistant. Be concise.')

result = agent.run_sync('What are the three laws of robotics?')
print(result.output)
