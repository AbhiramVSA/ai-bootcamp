# 02_structured_output.py
# Agent that returns structured data using Pydantic models.
# Run: uvicorn 02_structured_output:app --reload
# Try: curl -X POST http://localhost:8000/review -H "Content-Type: application/json" -d '{"movie": "Inception"}'

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent

app = FastAPI()


class MovieReview(BaseModel):
    title: str
    rating: float
    pros: list[str]
    cons: list[str]
    one_liner: str


agent = Agent(
    'openai:gpt-5-mini',
    result_type=MovieReview,
    system_prompt='You are a film critic. Analyze movies honestly. Rating is out of 10.',
)


class ReviewRequest(BaseModel):
    movie: str


@app.post('/review')
async def review(req: ReviewRequest):
    result = await agent.run(f'Review the movie: {req.movie}')
    return result.data
