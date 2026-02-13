# 06_debate_arena.py
# Multi-agent debate: two debaters argue, then a judge scores them.
# Run: uvicorn 06_debate_arena:app --reload
# Try: curl -X POST http://localhost:8000/debate -H "Content-Type: application/json" -d '{"topic": "Pineapple belongs on pizza"}'

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent

app = FastAPI()

debater_for = Agent(
    'openai:gpt-5-mini',
    system_prompt=(
        'You are a passionate, fiery debater who argues FOR the given position. '
        'You speak with conviction and use vivid language. You believe deeply in your side. '
        'Write 2-3 strong paragraphs. Do not hedge or equivocate.'
    ),
)

debater_against = Agent(
    'openai:gpt-5-mini',
    system_prompt=(
        'You are a cold, calculating debater who argues AGAINST the given position. '
        'You dismantle arguments with logic and precision. You are unimpressed by emotion. '
        'Write 2-3 sharp paragraphs. Be ruthlessly analytical.'
    ),
)

judge = Agent(
    'openai:gpt-5-mini',
    system_prompt=(
        'You are a fair, formal debate judge. You evaluate arguments on three criteria: '
        'Logic (soundness of reasoning), Persuasion (rhetorical effectiveness), and '
        'Evidence (use of facts and examples). Score each debater 1-10 on each criterion. '
        'Declare a winner. Be specific about why one side won.'
    ),
)


class DebateRequest(BaseModel):
    topic: str


@app.post('/debate')
async def debate(req: DebateRequest):
    # Round 1: Opening arguments
    for_result = await debater_for.run(f'Argue FOR: {req.topic}')
    against_result = await debater_against.run(f'Argue AGAINST: {req.topic}')

    # Round 2: Rebuttals (each debater sees the opponent's argument)
    for_rebuttal = await debater_for.run(
        f'Your opponent argued:\n\n{against_result.data}\n\nWrite a rebuttal defending your position FOR: {req.topic}'
    )
    against_rebuttal = await debater_against.run(
        f'Your opponent argued:\n\n{for_result.data}\n\nWrite a rebuttal defending your position AGAINST: {req.topic}'
    )

    # Judge evaluates everything
    transcript = (
        f'TOPIC: {req.topic}\n\n'
        f'=== FOR - Opening ===\n{for_result.data}\n\n'
        f'=== AGAINST - Opening ===\n{against_result.data}\n\n'
        f'=== FOR - Rebuttal ===\n{for_rebuttal.data}\n\n'
        f'=== AGAINST - Rebuttal ===\n{against_rebuttal.data}'
    )
    verdict = await judge.run(f'Judge this debate:\n\n{transcript}')

    return {
        'topic': req.topic,
        'for_opening': for_result.data,
        'against_opening': against_result.data,
        'for_rebuttal': for_rebuttal.data,
        'against_rebuttal': against_rebuttal.data,
        'verdict': verdict.data,
    }
