# 07_agent_pipeline.py
# Three agents chained in a pipeline: research -> write -> edit.
# Run: uvicorn 07_agent_pipeline:app --reload
# Try: curl -X POST http://localhost:8000/blog -H "Content-Type: application/json" -d '{"topic": "quantum computing"}'

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent

app = FastAPI()

researcher = Agent(
    'openai:gpt-5-mini',
    system_prompt='You are a research assistant. Given a topic, return exactly 5 key facts as a numbered list. Be specific and include numbers or dates where possible. No fluff.',
)

writer = Agent(
    'openai:gpt-5-mini',
    system_prompt='You are a blog writer. Given a list of facts, write a short, engaging blog post (200-300 words). Make it accessible to a general audience. Do not add a title.',
)

editor = Agent(
    'openai:gpt-5-mini',
    system_prompt='You are a senior editor. Given a blog draft, improve the writing for clarity and flow. Add a catchy title. Return the final version with the title on the first line.',
)


class BlogRequest(BaseModel):
    topic: str


@app.post('/blog')
async def blog(req: BlogRequest):
    # Stage 1: Research
    research_result = await researcher.run(f'Research this topic: {req.topic}')
    facts = research_result.data

    # Stage 2: Write
    write_result = await writer.run(f'Write a blog post based on these facts:\n\n{facts}')
    draft = write_result.data

    # Stage 3: Edit
    edit_result = await editor.run(f'Edit and improve this blog draft:\n\n{draft}')
    final = edit_result.data

    return {
        'facts': facts,
        'draft': draft,
        'final': final,
    }
