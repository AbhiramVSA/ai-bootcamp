<p align="center">
  <img src="assets/ai-agents-bootcamp-mark.png" alt="Three connected AI agent nodes branching from a prompt" width="128" />
</p>

<h1 align="center">AI Agents Bootcamp</h1>

<p align="center">A practical introduction to prompt engineering and AI agents through ten Python examples, a reference guide, and an interactive presentation.</p>

<p align="center">
  <a href="#start-here">Start here</a> ·
  <a href="#examples">Examples</a> ·
  <a href="#course-material">Course material</a> ·
  <a href="#license">License</a>
</p>

## Start here

The examples use PydanticAI and FastAPI. The unified server exposes the web examples in one API and serves a small browser dashboard.

**Requirements:** Python 3.13 or later and an OpenAI API key.

```bash
git clone https://github.com/AbhiramVSA/ai-bootcamp.git
cd ai-bootcamp
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt 'fastapi<0.142'
```

Set `OPENAI_API_KEY` in the environment or in a `.env` file in the repository root. Start the unified API:

```bash
uvicorn main:app --reload
```

Open [the API docs](http://localhost:8000/docs), [the example dashboard](http://localhost:8000/ui), or [the presentation](http://localhost:8000/static/presentation.html).

## Examples

| # | Example | Topic | Unified API route |
|---|---|---|---|
| 01 | `01_basic_agent.py` | Minimal agent | Run as a script |
| 02 | `02_structured_output.py` | Typed model output | `POST /review` |
| 03 | `03_tools_agent.py` | Tool calls | `POST /ask` |
| 04 | `04_deps_agent.py` | Runtime dependencies and instructions | `POST /assist` |
| 05 | `05_streaming.py` | Streamed response | `GET /story?topic=` |
| 06 | `06_debate_arena.py` | Multi-agent debate | `POST /debate` |
| 07 | `07_agent_pipeline.py` | Three-stage agent pipeline | `POST /blog` |
| 08 | `08_roast_my_code.py` | Code review agent | `POST /roast` |
| 09 | `09_whisper_agent.py` | Audio transcription and analysis | `POST /transcribe` |
| 10 | `10_memory_chat.py` | Stateful conversation | `POST /chat`, `GET /history/{session_id}` |

Example request:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Roll two dice and add the results"}'
```

You can also run one API example directly. For example:

```bash
uvicorn 02_structured_output:app --reload
```

## Course material

- [`static/presentation.html`](static/presentation.html) — interactive slides on prompting and AI agents
- [`static/index.html`](static/index.html) — browser dashboard for the examples
- [`prompting-techniques.md`](prompting-techniques.md) — written reference guide
- [`KERNEL_PROMPT.md`](KERNEL_PROMPT.md) — prompt design notes

## Stack

Python, PydanticAI, Pydantic, FastAPI, Uvicorn, and the OpenAI API.

## License

This repository is provided for educational purposes. It does not include a license file.
