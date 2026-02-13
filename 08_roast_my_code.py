# 08_roast_my_code.py
# A brutally honest (but funny) code review agent.
# Run: uvicorn 08_roast_my_code:app --reload
# Try: curl -X POST http://localhost:8000/roast -H "Content-Type: application/json" -d '{"code": "def add(a,b): return a+b"}'

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent

app = FastAPI()


class RoastResult(BaseModel):
    roast: str
    score: int
    issues: list[str]
    compliment: str


agent = Agent(
    'openai:gpt-5-mini',
    result_type=RoastResult,
    system_prompt=(
        'You are the Gordon Ramsay of code review. You roast code with dramatic flair. '
        'You are brutally honest but technically accurate. '
        'Point out REAL issues (bugs, bad practices, security problems, style issues). '
        'Be over-the-top dramatic about it - act personally offended by bad code. '
        'Score from 1 (dumpster fire) to 10 (perfection). '
        'Always end with exactly one genuine, specific compliment.'
    ),
)


class CodeRequest(BaseModel):
    code: str


@app.post('/roast')
async def roast(req: CodeRequest):
    result = await agent.run(f'Roast this code:\n\n```\n{req.code}\n```')
    return result.data
