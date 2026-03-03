# AI Agents Bootcamp

A hands-on bootcamp covering prompt engineering foundations and practical AI agent development using PydanticAI and FastAPI.

The bootcamp includes an interactive slide deck on prompting techniques, a written reference guide, and 10 progressive Python examples that build from a minimal agent to multi-agent orchestration, streaming, audio transcription, and stateful conversation.

## Contents

### Presentation

- `static/presentation.html` -- Interactive HTML slide deck covering prompting techniques and AI agents
- `static/index.html` -- Agent dashboard UI for testing all example endpoints
- `prompting-techniques.md` -- Full written reference guide

### Examples

| #  | File                      | Concept                  | Endpoint                     |
|----|---------------------------|--------------------------|------------------------------|
| 01 | `01_basic_agent.py`       | Minimal agent            | CLI only                     |
| 02 | `02_structured_output.py` | Pydantic model output    | `POST /review`               |
| 03 | `03_tools_agent.py`       | Function calling / tools | `POST /ask`                  |
| 04 | `04_deps_agent.py`        | Runtime dependencies     | `POST /assist`               |
| 05 | `05_streaming.py`         | Streaming responses      | `GET /story?topic=`          |
| 06 | `06_debate_arena.py`      | Multi-agent debate       | `POST /debate`               |
| 07 | `07_agent_pipeline.py`    | Three-stage pipeline     | `POST /blog`                 |
| 08 | `08_roast_my_code.py`     | Code review agent        | `POST /roast`                |
| 09 | `09_whisper_agent.py`     | Audio transcription + AI | `POST /transcribe`           |
| 10 | `10_memory_chat.py`       | Stateful conversation    | `POST /chat`, `GET /history` |

## Prerequisites

- Python 3.13 or higher
- An OpenAI API key

## Setup

```bash
# Clone the repository
git clone https://github.com/AbhiramVSA/ai-bootcamp.git
cd ai-bootcamp

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Configure your API key
echo "OPENAI_API_KEY=your-key-here" > .env
```

If you use [uv](https://github.com/astral-sh/uv) you can replace the venv and pip steps with:

```bash
uv sync
```

## Running the Presentation

Open the slide deck directly in any browser:

```
static/presentation.html
```

Or serve it through the FastAPI server (see below) and visit:

```
http://localhost:8000/static/presentation.html
```

## Running the Examples

### Unified server (recommended)

Start the server that exposes all example endpoints at once:

```bash
uvicorn main:app --reload
```

Then open:

- API docs (Swagger UI): http://localhost:8000/docs
- Agent dashboard: http://localhost:8000/ui
- Presentation: http://localhost:8000/static/presentation.html

### Individual examples

Run any single example as a standalone FastAPI app:

```bash
uvicorn 02_structured_output:app --reload
```

Example 01 runs directly as a script:

```bash
python 01_basic_agent.py
```

### Sample request

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Roll two dice and add the results"}'
```

## Tech Stack

- **PydanticAI** -- agent framework
- **FastAPI** -- web framework and auto-generated API docs
- **Uvicorn** -- ASGI server
- **Pydantic** -- data validation and structured output
- **OpenAI API** -- LLM provider

## Author

**Abhiram** -- [github.com/AbhiramVSA](https://github.com/AbhiramVSA)

## License

This project is provided for educational purposes.
