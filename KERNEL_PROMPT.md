# KERNEL Prompt — AI Agents Bootcamp Overhaul

Copy everything below the line and paste it into Claude Opus 4.6.

---

## Knowledge

I'm running an AI bootcamp. I have an existing markdown document `prompting-techniques.md` that covers prompt engineering in sections 1-10. Sections 1-3 are great and should stay. Sections 4-10 are redundant prompt engineering content I want to replace entirely.

The new content must cover **AI Agents** — theory first, then hands-on code. All practical examples use **PydanticAI** (https://ai.pydantic.dev/) as the agent framework and **FastAPI** for serving endpoints. I have an **OpenAI API key** set as `OPENAI_API_KEY` environment variable.

Here is what you need to know about PydanticAI:

**Core Agent Pattern:**
```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-5-mini', instructions='You are a helpful assistant.')
result = agent.run_sync('Hello')
print(result.output)
```

**Structured Output:**
```python
from pydantic import BaseModel
from pydantic_ai import Agent

class City(BaseModel):
    name: str
    country: str
    population: int

agent = Agent('openai:gpt-5-mini', output_type=City)
result = agent.run_sync('Tell me about Paris')
print(result.output)  # City(name='Paris', country='France', population=2161000)
```

**Tools (agent can call functions):**
```python
from pydantic_ai import Agent, RunContext

agent = Agent('openai:gpt-5-mini')

@agent.tool_plain
def roll_dice(sides: int = 6) -> int:
    """Roll a die."""
    import random
    return random.randint(1, sides)

result = agent.run_sync('Roll a 20-sided die')
```

**Tools with Dependencies:**
```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class Deps:
    user_name: str

agent = Agent('openai:gpt-5-mini', deps_type=Deps)

@agent.tool
def greet(ctx: RunContext[Deps]) -> str:
    """Get the user's name."""
    return f"The user's name is {ctx.deps.user_name}"

result = agent.run_sync('Say hi to me', deps=Deps(user_name='Abhi'))
```

**Dynamic Instructions:**
```python
@agent.instructions
def custom_instructions(ctx: RunContext[Deps]) -> str:
    return f"The user's name is {ctx.deps.user_name}. Be friendly."
```

**Streaming:**
```python
import asyncio
from pydantic_ai import Agent

agent = Agent('openai:gpt-5-mini')

async def main():
    async with agent.run_stream('Tell me a joke') as response:
        async for chunk in response.stream_text(delta=True):
            print(chunk, end='', flush=True)

asyncio.run(main())
```

**Multi-Agent via tool delegation:**
```python
researcher = Agent('openai:gpt-5-mini', instructions='You research topics.')
writer = Agent('openai:gpt-5-mini', instructions='You write content.')

@writer.tool
async def research(ctx: RunContext[None], topic: str) -> str:
    """Research a topic before writing."""
    result = await researcher.run(f'Research: {topic}', usage=ctx.usage)
    return result.output
```

**Multi-Agent via programmatic hand-off (passing message_history):**
```python
result1 = await agent_a.run('Do step 1')
result2 = await agent_b.run('Do step 2', message_history=result1.new_messages())
```

**Conversation history:**
```python
result1 = agent.run_sync('My name is Abhi')
result2 = agent.run_sync('What is my name?', message_history=result1.new_messages())
```

**FastAPI integration:**
```python
from fastapi import FastAPI
from pydantic_ai import Agent

app = FastAPI()
agent = Agent('openai:gpt-5-mini')

@app.post('/chat')
async def chat(prompt: str):
    result = await agent.run(prompt)
    return {'response': result.output}
```

**Streaming with FastAPI:**
```python
from fastapi.responses import StreamingResponse

@app.post('/stream')
async def stream(prompt: str):
    async def generate():
        async with agent.run_stream(prompt) as response:
            async for chunk in response.stream_text(delta=True):
                yield chunk
    return StreamingResponse(generate(), media_type='text/plain')
```

**ModelRetry for error handling in tools:**
```python
from pydantic_ai import ModelRetry

@agent.tool(retries=3)
def find_user(ctx: RunContext[Deps], name: str) -> str:
    """Find a user."""
    user = lookup(name)
    if not user:
        raise ModelRetry(f'No user "{name}". Try a different name.')
    return user
```

**Install command:**
```bash
pip install pydantic-ai fastapi uvicorn
```

## Expectation

You must produce the following deliverables:

### 1. Replace sections 4-10 in `prompting-techniques.md`

Keep sections 1, 2, and 3 exactly as they are. Replace everything from section 4 onwards with new content structured as:

**Section 4: From Prompts to Agents — The Theory**
- What is an AI agent? (LLM + tools + loop + memory)
- The ReAct loop revisited — agents are ReAct made real
- Agent architectures: single agent, multi-agent delegation, pipelines, orchestrator patterns
- When to use agents vs. plain prompts
- Diagram: The anatomy of an agent (LLM brain + tools + memory + orchestration)

**Section 5: Hands-On — Building Agents with PydanticAI**
- Brief intro to PydanticAI (why this framework — type-safe, Pydantic validation, multi-model)
- Setup instructions (pip install, env var)
- Link to each Python file created below with a 2-3 sentence description of what it does and what concept it teaches

**Section 6: Quick Reference — Agent Patterns**
- Table mapping patterns to files (single agent → file, multi-agent → file, etc.)
- Mental models for agents

Update the table of contents to reflect these new sections.

### 2. Create these Python files in the root directory

Each file must be **self-contained, simple, and runnable** with just `python filename.py` or `uvicorn filename:app --reload`. No subdirectories. No complex project structure. Everything flat in the root.

**All files use `openai:gpt-5-mini` as the model** (user has an OpenAI key).

Here are the files to create:

---

#### `01_basic_agent.py` — Hello World Agent
A bare minimum PydanticAI agent. Run it, it prints a response. Teaches: Agent creation, `run_sync`.

---

#### `02_structured_output.py` — Structured Output Agent
Agent that analyzes a movie and returns a structured `MovieReview` Pydantic model with title, rating, pros, cons, one_liner. FastAPI endpoint: `POST /review` accepts `{"movie": "Inception"}` and returns the structured JSON. Teaches: structured output, Pydantic models as output types.

---

#### `03_tools_agent.py` — Agent with Tools
An agent that can use tools. Give it 2-3 fun tools:
- `roll_dice(sides)` — rolls a die
- `get_time()` — returns current time
- `calculate(expression)` — evaluates a math expression (use `ast.literal_eval` or simple parsing, NOT raw `eval`)

FastAPI endpoint: `POST /ask` accepts `{"question": "..."}`. The agent decides which tools to call. Teaches: tool use, how the agent autonomously picks tools.

---

#### `04_deps_agent.py` — Agent with Dependencies
An agent that receives runtime dependencies. Build a "personalized assistant" where the user's name and preferences are injected as deps. The agent uses dynamic instructions based on the deps.

FastAPI endpoint: `POST /assist` accepts `{"user_name": "Abhi", "style": "pirate", "question": "What should I eat for lunch?"}`. The agent answers in the user's preferred style. Teaches: dependency injection, dynamic instructions.

---

#### `05_streaming.py` — Streaming Agent
An agent that streams a story in real-time. FastAPI endpoint: `GET /story?topic=dragons` returns a `StreamingResponse` that streams the story token by token. Teaches: streaming responses, SSE-like patterns.

---

#### `06_debate_arena.py` — Multi-Agent Debate (THE WOW DEMO)
Three agents: `debater_for`, `debater_against`, `judge`. Given a topic:
1. `debater_for` argues FOR the topic (2-3 paragraphs)
2. `debater_against` argues AGAINST (2-3 paragraphs)
3. Each debater gets one rebuttal round (they see the opponent's argument via message passing)
4. `judge` reads all arguments and scores each debater on logic, persuasion, evidence. Declares a winner.

FastAPI endpoint: `POST /debate` accepts `{"topic": "Pineapple belongs on pizza"}`. Returns the full debate transcript with the judge's verdict. Teaches: multi-agent systems, message passing, agent delegation.

---

#### `07_agent_pipeline.py` — Sequential Agent Pipeline
A content pipeline: three agents chained together.
1. `researcher` — takes a topic, outputs 5 key facts
2. `writer` — takes the facts, writes a short blog post
3. `editor` — takes the blog post, improves it, adds a catchy title

FastAPI endpoint: `POST /blog` accepts `{"topic": "quantum computing"}`. Returns `{"facts": [...], "draft": "...", "final": {"title": "...", "content": "..."}}` showing each stage. Teaches: sequential agent pipelines, output of one agent feeding the next.

---

#### `08_roast_my_code.py` — Code Roaster Agent (FUN DEMO)
An agent with the persona of a brutally honest (but funny) senior engineer who roasts your code. Think Gordon Ramsay but for code. It should:
- Point out actual issues (bugs, bad practices)
- Be dramatically over-the-top about it
- Give a "roast score" from 1-10 (10 = perfect code, 1 = dumpster fire)
- End with one genuine compliment

FastAPI endpoint: `POST /roast` accepts `{"code": "def add(a,b): return a+b"}`. Returns structured output with roast text, score, issues found, and the compliment. Teaches: persona-driven agents, structured output, entertainment value.

---

#### `09_whisper_agent.py` — Audio Transcription + Agent Pipeline
Uses OpenAI's Whisper API to transcribe an audio file, then passes the transcript to a PydanticAI agent that:
- Summarizes what was said
- Extracts action items
- Identifies the overall sentiment

FastAPI endpoint: `POST /transcribe` accepts a file upload (audio file). Returns `{"transcript": "...", "summary": "...", "action_items": [...], "sentiment": "..."}`. Use `openai` Python package directly for the Whisper call, then PydanticAI for the analysis agent. Teaches: combining traditional APIs with agents, real-world pipeline.

---

#### `10_memory_chat.py` — Agent with Conversation Memory
A chat agent that maintains conversation history across multiple requests using an in-memory dict keyed by session_id.

FastAPI endpoints:
- `POST /chat` accepts `{"session_id": "abc", "message": "My name is Abhi"}` — sends message and gets response
- `GET /history/{session_id}` — returns conversation history

The agent remembers previous messages in the session. Teaches: conversation memory, stateful agents.

---

#### `requirements.txt`
Just the dependencies needed:
```
pydantic-ai
fastapi
uvicorn
openai
python-multipart
```

---

## Role

You are a senior AI engineer and technical instructor creating bootcamp materials. You write clean, minimal Python code that just works. You explain complex concepts simply. Your code examples are designed to be run live in front of an audience — they must be impressive but dead simple.

## Nuance

- Every Python file must have a brief comment block at the top explaining what it does and how to run it
- Use `openai:gpt-5-mini` as the model everywhere — the user has an OpenAI key
- Do NOT use `eval()` anywhere — use `ast.literal_eval` or a safe alternative for the calculator tool
- Keep files SHORT. Each file should be under 120 lines ideally. Simpler is better.
- Do NOT create subdirectories. Everything goes in the project root.
- Do NOT add type: ignore comments or excessive error handling. Keep it clean.
- For the audio transcription example, use the `openai` package directly (`openai.audio.transcriptions.create`) since PydanticAI doesn't wrap Whisper
- For streaming endpoints, use `StreamingResponse` from FastAPI
- The debate arena is the showstopper demo — make it dramatic and fun. Give the debaters strong, contrasting personas.
- In the markdown document, use the same visual style as sections 1-3 (ASCII diagrams, comparison tables, "Try This" exercises)
- Make sure the markdown theory section explains agents in a way that builds on the ReAct pattern already covered in section 2.4 — connect the concepts
- Do NOT include any API keys in the code. Use `os.getenv('OPENAI_API_KEY')` or let PydanticAI pick it up automatically from the environment
- `python-multipart` is needed for FastAPI file uploads in the whisper example
- All FastAPI apps should be named `app` so they can be run with `uvicorn filename:app --reload`
- For the safe calculator in `03_tools_agent.py`, you can use `ast.literal_eval` for simple expressions, or use the `operator` module to build a minimal safe evaluator. Keep it simple — it only needs to handle basic arithmetic.

## Examples

Here is the style of code I want — minimal, no fluff:

```python
# 01_basic_agent.py
# The simplest possible PydanticAI agent
# Run: python 01_basic_agent.py

from pydantic_ai import Agent

agent = Agent('openai:gpt-5-mini', instructions='You are a helpful assistant. Be concise.')

result = agent.run_sync('What is the meaning of life?')
print(result.output)
```

That's the vibe. Short. Runs. Impressive.

For FastAPI endpoints, this style:

```python
from fastapi import FastAPI
from pydantic_ai import Agent
from pydantic import BaseModel

app = FastAPI()
agent = Agent('openai:gpt-5-mini')

class Query(BaseModel):
    question: str

@app.post('/ask')
async def ask(query: Query):
    result = await agent.run(query.question)
    return {'answer': result.output}
```

For the markdown theory section, match the existing style with ASCII diagrams like:

```
┌─────────────────────────────────────────────────────────┐
│                   THE AI AGENT                           │
│                                                          │
│  ┌──────────┐                                            │
│  │   LLM    │ ◄── The "brain" - reasons about tasks      │
│  │  (Brain) │                                            │
│  └────┬─────┘                                            │
│       │                                                  │
│  ┌────▼─────┐                                            │
│  │  TOOLS   │ ◄── Functions the agent can call            │
│  │          │     (search, calculate, APIs)               │
│  └────┬─────┘                                            │
│       │                                                  │
│  ┌────▼─────┐                                            │
│  │  MEMORY  │ ◄── Conversation history, state             │
│  └────┬─────┘                                            │
│       │                                                  │
│  ┌────▼─────┐                                            │
│  │   LOOP   │ ◄── Observe → Think → Act → Repeat         │
│  └──────────┘                                            │
└─────────────────────────────────────────────────────────┘
```

## Language

- Code comments: casual, brief, no fluff
- Markdown content: professional but accessible, same tone as sections 1-3
- Agent personas in the code: colorful and fun (especially the code roaster and debaters)
- Technical terms: explain on first use, then use freely
- No emojis in any files
