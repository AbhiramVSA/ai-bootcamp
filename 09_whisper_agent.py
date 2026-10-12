# 09_whisper_agent.py
# Transcribe audio with Whisper, then analyze with a PydanticAI agent.
# Run: uvicorn 09_whisper_agent:app --reload
# Try: curl -X POST http://localhost:8000/transcribe -F "file=@recording.mp3"

from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from pydantic_ai import Agent
from openai import AsyncOpenAI

from settings import settings

app = FastAPI()
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class TranscriptAnalysis(BaseModel):
    summary: str
    action_items: list[str]
    sentiment: str


agent = Agent(
    'openai:gpt-5-mini',
    output_type=TranscriptAnalysis,
    system_prompt=(
        'You analyze meeting transcripts. Extract a concise summary, '
        'a list of action items (things people committed to doing), '
        'and the overall sentiment (positive, negative, neutral, or mixed).'
    ),
)


@app.post('/transcribe')
async def transcribe(file: UploadFile):
    # Step 1: Transcribe with Whisper
    transcript = await openai_client.audio.transcriptions.create(
        model='whisper-1',
        file=(file.filename, await file.read(), file.content_type),
    )

    # Step 2: Analyze with PydanticAI agent
    result = await agent.run(f'Analyze this transcript:\n\n{transcript.text}')

    return {
        'transcript': transcript.text,
        'summary': result.output.summary,
        'action_items': result.output.action_items,
        'sentiment': result.output.sentiment,
    }
