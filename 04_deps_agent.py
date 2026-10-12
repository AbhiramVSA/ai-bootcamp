# 04_deps_agent.py
# Agent with runtime dependencies and dynamic instructions.
# Run: uvicorn 04_deps_agent:app --reload
# Try: curl -X POST http://localhost:8000/assist -H "Content-Type: application/json" -d '{"user_name": "Abhi", "style": "pirate", "question": "What should I eat for lunch?"}'

from dataclasses import dataclass

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

app = FastAPI()


@dataclass
class UserDeps:
    user_name: str
    style: str


agent = Agent('openai:gpt-5-mini', deps_type=UserDeps)


@agent.system_prompt
def custom_instructions(ctx: RunContext[UserDeps]) -> str:
    return (
        f"The user's name is {ctx.deps.user_name}. "
        f"Respond in the style of a {ctx.deps.style}. "
        f"Stay in character no matter what. Keep it fun but helpful."
    )


class AssistRequest(BaseModel):
    user_name: str
    style: str
    question: str


@app.post('/assist')
async def assist(req: AssistRequest):
    deps = UserDeps(user_name=req.user_name, style=req.style)
    result = await agent.run(req.question, deps=deps)
    return {'answer': result.output}
