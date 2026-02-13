# 05_streaming.py
# Agent that streams responses token by token.
# Run: uvicorn 05_streaming:app --reload
# Try: curl http://localhost:8000/story?topic=dragons

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic_ai import Agent

app = FastAPI()

agent = Agent(
    'openai:gpt-5-mini',
    system_prompt='You are a creative storyteller. Write vivid, engaging short stories (about 200 words).',
)


@app.get('/story')
async def story(topic: str = 'a mysterious door'):
    async def generate():
        async with agent.run_stream(f'Write a short story about: {topic}') as response:
            async for chunk in response.stream_text(delta=True):
                yield chunk

    return StreamingResponse(generate(), media_type='text/plain')
