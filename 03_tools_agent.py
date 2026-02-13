# 03_tools_agent.py
# Agent that autonomously decides which tools to call.
# Run: uvicorn 03_tools_agent:app --reload
# Try: curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question": "What time is it and roll me a d20?"}'

import ast
import random
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent

app = FastAPI()

agent = Agent(
    'openai:gpt-5-mini',
    system_prompt='You are a helpful assistant with access to tools. Use them when relevant.',
)


@agent.tool_plain
def roll_dice(sides: int = 6, count: int = 1) -> str:
    """Roll one or more dice with the given number of sides."""
    rolls = [random.randint(1, sides) for _ in range(count)]
    if count == 1:
        return f'Rolled a d{sides}: {rolls[0]}'
    return f'Rolled {count}d{sides}: {rolls}'


@agent.tool_plain
def get_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


@agent.tool_plain
def calculate(expression: str) -> str:
    """Evaluate a simple math expression like '2 + 3 * 4'. Only basic arithmetic is supported."""
    try:
        tree = ast.parse(expression, mode='eval')
        # Walk the AST to ensure only safe operations are present
        for node in ast.walk(tree):
            if isinstance(node, (ast.Call, ast.Import, ast.ImportFrom)):
                return f'Disallowed operation in expression: {expression}'
            if isinstance(node, ast.Attribute):
                return f'Attribute access not allowed: {expression}'
        code = compile(tree, '<string>', 'eval')
        result = eval(code, {"__builtins__": {}})
        return str(result)
    except Exception:
        return f'Could not evaluate: {expression}'


class AskRequest(BaseModel):
    question: str


@app.post('/ask')
async def ask(req: AskRequest):
    result = await agent.run(req.question)
    return {'answer': result.data}
