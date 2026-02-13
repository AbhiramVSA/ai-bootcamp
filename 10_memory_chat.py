# 10_memory_chat.py
# Chat agent that remembers conversation history per session.
# Run: uvicorn 10_memory_chat:app --reload
# Try: curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"session_id": "abc", "message": "My name is Abhi"}'
# Then: curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"session_id": "abc", "message": "What is my name?"}'

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

app = FastAPI()

agent = Agent(
    'openai:gpt-5-mini',
    system_prompt='You are a friendly assistant. Remember details the user shares with you.',
)

# In-memory session store
sessions: dict[str, list[ModelMessage]] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post('/chat')
async def chat(req: ChatRequest):
    history = sessions.get(req.session_id, [])
    result = await agent.run(req.message, message_history=history)
    sessions[req.session_id] = result.all_messages()
    return {'response': result.data}


@app.get('/history/{session_id}')
async def history(session_id: str):
    messages = sessions.get(session_id, [])
    return {
        'session_id': session_id,
        'message_count': len(messages),
        'messages': [
            {'role': msg.role, 'content': str(msg)}
            for msg in messages
            if hasattr(msg, 'role')
        ],
    }
