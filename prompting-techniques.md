# Prompting Techniques and AI Agents

> **A practical guide for the LLM Bootcamp** — covering prompt engineering foundations, advanced reasoning techniques, and hands-on AI agent development with PydanticAI.

This document is split into two parts. **Part 1** covers prompt engineering — how to write effective instructions for LLMs. **Part 2** covers AI agents — how to build systems where LLMs can use tools, maintain memory, and work together.

---

## Table of Contents

**Part 1 — Prompt Engineering**
1. [Types of Prompting](#1-types-of-prompting)
2. [Advanced Prompting Techniques](#2-advanced-prompting-techniques)
3. [Prompt Structure and Frameworks](#3-prompt-structure-and-frameworks)

**Part 2 — AI Agents**
4. [From Prompts to Agents — The Theory](#4-from-prompts-to-agents--the-theory)
5. [Hands-On — Building Agents with PydanticAI](#5-hands-on--building-agents-with-pydanticai)
6. [Quick Reference — Agent Patterns](#6-quick-reference--agent-patterns)

---

## 1. Types of Prompting

There are three foundational prompting strategies. Each gives the model a different amount of guidance. Choosing the right one depends on task complexity and how predictable you need the output to be.

```
┌─────────────────────────────────────────────────────────────────┐
│                   PROMPTING SPECTRUM                            │
│                                                                 │
│  Zero-Shot ──────── Few-Shot ──────── Structured                │
│  (no examples)      (2-5 examples)    (schema + examples        │
│                                        + constraints)           │
│                                                                 │
│  Less guidance ──────────────────────► More guidance             │
│  Less predictable ───────────────────► More predictable         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.1 Zero-Shot Prompting

Zero-shot prompting means giving the model a task with **no examples**. You rely entirely on the model's pre-existing knowledge to interpret your intent.

**When to use it:** Simple, well-defined tasks where the expected output format is obvious.

```text
Classify the following movie review as POSITIVE, NEGATIVE, or NEUTRAL.

Review: "The cinematography was breathtaking, but the plot felt rushed
and predictable."
```

**Expected output:**
```
NEUTRAL
```

Zero-shot works well when:
- The task is common (summarization, classification, translation)
- The output format is simple (a single label, a yes/no answer)
- Ambiguity is low

> **Warning:** Zero-shot prompts fail silently. The model will always produce *something*, even if it misunderstands the task. You won't get an error — you'll get a confident wrong answer.

---

### 1.2 Few-Shot Prompting

Few-shot prompting includes **2–5 examples** of input-output pairs before your actual query. The examples teach the model the pattern you expect.

```text
Extract the product name and price from each sentence.

Sentence: "The new AirPods Max are available for $549."
Product: AirPods Max
Price: $549

Sentence: "You can get the Galaxy S24 Ultra starting at $1,299."
Product: Galaxy S24 Ultra
Price: $1,299

Sentence: "The Kindle Paperwhite is on sale for $129."
```

**Expected output:**
```
Product: Kindle Paperwhite
Price: $129
```

**Key principles for few-shot examples:**

| Principle | Why It Matters |
|-----------|---------------|
| **Diversity** | Cover edge cases (e.g., different formats, missing data) |
| **Consistency** | Use identical formatting across all examples |
| **Relevance** | Examples should match the actual task distribution |
| **Order** | Place the hardest or most representative example last |

> **Insight:** Few-shot prompting is not "training" the model. You are activating patterns the model already knows by showing it what success looks like in context.

---

### 1.3 Structured Prompting

Structured prompting combines explicit instructions, formatting rules, examples, and constraints into a single, organized prompt. It is the most reliable approach for complex or high-stakes tasks.

```text
You are a data extraction assistant.

## Task
Extract all company names, their founding years, and headquarters
locations from the provided text. If a field is missing, write "N/A".

## Output Format
Return a JSON array. Each object must have these keys:
- "company" (string)
- "founded" (integer or "N/A")
- "headquarters" (string or "N/A")

## Example
Input: "Apple was founded in 1976 and is based in Cupertino.
SpaceX, headquartered in Hawthorne, was started in 2002."

Output:
[
  {"company": "Apple", "founded": 1976, "headquarters": "Cupertino"},
  {"company": "SpaceX", "founded": 2002, "headquarters": "Hawthorne"}
]

## Text to Process
"Microsoft was founded by Bill Gates and Paul Allen in 1975.
The company is headquartered in Redmond, Washington.
Stripe is based in San Francisco."
```

Structured prompting is the default choice for production systems, automated pipelines, and any scenario where output consistency matters.

---

### Comparison of Prompting Types

| Aspect | Zero-Shot | Few-Shot | Structured |
|--------|-----------|----------|------------|
| Examples provided | None | 2–5 | 1+ with full schema |
| Setup effort | Low | Medium | High |
| Output consistency | Variable | Good | Excellent |
| Best for | Simple tasks | Pattern matching | Production systems |
| Risk of misinterpretation | High | Medium | Low |

---

### Try This: Zero-Shot vs. Few-Shot

Run both prompts and compare the outputs.

**Zero-shot version:**
```text
Convert this sentence to formal business English:
"Hey, just wanted to check if you guys got my email about the project thing."
```

**Few-shot version:**
```text
Convert informal sentences to formal business English.

Informal: "Can you send that over ASAP? We need it like yesterday."
Formal: "Could you please send that document at your earliest
convenience? It is needed urgently."

Informal: "I'm gonna skip the meeting, not feeling great."
Formal: "I will be unable to attend the meeting today due to
a health concern."

Informal: "Hey, just wanted to check if you guys got my email
about the project thing."
Formal:
```

Notice how the few-shot version produces output that matches the tone, length, and structure of your examples.

---

## 2. Advanced Prompting Techniques

Beyond the basics, there are powerful techniques that unlock reasoning, self-correction, and multi-step problem solving. These are the techniques that separate surface-level prompt writing from real prompt engineering.

```
┌──────────────────────────────────────────────────────────────────┐
│              ADVANCED TECHNIQUE MAP                              │
│                                                                  │
│  Chain-of-Thought (CoT)                                         │
│    └── "Think step by step"                                     │
│         ├── Self-Consistency  (multiple CoT paths → vote)       │
│         └── Tree of Thoughts  (branching + backtracking)        │
│                                                                  │
│  ReAct                                                           │
│    └── Thought → Action → Observation → repeat                  │
│                                                                  │
│  RAG (Retrieval-Augmented Generation)                            │
│    └── Retrieve context → Inject into prompt → Generate         │
│                                                                  │
│  Meta Prompting                                                  │
│    └── Prompt about the structure of prompts                    │
└──────────────────────────────────────────────────────────────────┘
```

### 2.1 Chain-of-Thought (CoT) Prompting

Chain-of-Thought prompting asks the model to **show its reasoning step by step** before arriving at an answer. Introduced by Wei et al. (2022), it dramatically improves performance on math, logic, and multi-step reasoning tasks.

**Why it works:** When a model jumps straight to an answer, it can skip over intermediate logic — especially on problems with multiple interacting conditions. When forced to write out its reasoning, each step constrains the next, and errors surface before they compound into a wrong final answer.

> **A note on the original research:** The CoT paper (Wei et al., 2022) used simple arithmetic examples where earlier models failed without step-by-step prompting. Modern models like GPT-4o and Claude handle basic arithmetic fine without CoT. The technique's value today is on **harder, multi-step problems** — the kind where even strong models benefit from structured reasoning.

**Without CoT (direct answer):**
```text
A farmer has 3 fields. Field A produces 20% more wheat than Field B.
Field C produces 15% less than Field A. Together, all three fields
produce 680 tons. How much does each field produce?
```
*Models often guess or give rounded approximations — the answer varies across runs.*

**With CoT (step-by-step reasoning):**
```text
A farmer has 3 fields. Field A produces 20% more wheat than Field B.
Field C produces 15% less than Field A. Together, all three fields
produce 680 tons. How much does each field produce?

Work through this step by step, showing all equations.
```
Model output:
```
Let B = tons from Field B.
Field A = 1.20 x B
Field C = 0.85 x Field A = 0.85 x 1.20 x B = 1.02 x B

Total: B + 1.20B + 1.02B = 680
3.22B = 680
B = 211.18 tons

Field A = 1.20 x 211.18 = 253.42 tons
Field C = 1.02 x 211.18 = 215.40 tons

Check: 211.18 + 253.42 + 215.40 = 680
```

The difference is not just accuracy — it is **verifiability**. With CoT, you can check each step. Without it, you get a number and have to trust it.

**Zero-Shot CoT — the simplest version:**

You don't need examples. Just add **"Let's think step by step"** to the end of any prompt. This single phrase activates step-by-step reasoning in most modern models.

```text
In a room, there are 4 people. Each person shakes hands with every
other person exactly once. Then 2 more people enter and shake hands
with everyone in the room (including each other). How many total
handshakes occurred?

Let's think step by step.
```

Without this phrase, models frequently miscalculate multi-stage combinatorics. With it, they break the problem into phases and apply the combination formula correctly at each stage.

> **Key takeaway:** CoT is not about making the model "smarter." It is about giving the model scratch paper. Humans solve complex problems by writing down intermediate steps. LLMs work the same way — and the harder the problem, the more CoT matters.

---

### 2.2 Self-Consistency

Self-Consistency (Wang et al., 2022) improves on Chain-of-Thought by generating **multiple independent reasoning paths** and then taking a **majority vote** on the final answer.

```
┌──────────────────────────────────────────────────────────────┐
│                   SELF-CONSISTENCY                            │
│                                                              │
│  Same prompt ──┬── Path 1 → Answer: 42                      │
│                ├── Path 2 → Answer: 42                      │
│                ├── Path 3 → Answer: 38                      │
│                ├── Path 4 → Answer: 42                      │
│                └── Path 5 → Answer: 42                      │
│                                                              │
│  Majority vote → Final answer: 42  (4 out of 5 agree)      │
└──────────────────────────────────────────────────────────────┘
```

**Why it works:** A single CoT path can contain a reasoning error. But if you run 5 independent CoT paths, and 4 of them reach the same answer, the probability that answer is correct goes up significantly. It's error correction through redundancy.

**When to use it:** Math problems, logical reasoning, any task where there's a single correct answer and you can afford to run the prompt multiple times.

**How to implement it:**
1. Run the same CoT prompt 5 times (with a temperature > 0 to get varied reasoning)
2. Extract the final answer from each run
3. Pick the answer that appears most frequently

---

### 2.3 Tree of Thoughts (ToT)

Tree of Thoughts (Yao et al., 2023) generalizes CoT from a single chain to a **branching tree** of reasoning paths. At each step, the model generates multiple candidate "thoughts," evaluates which ones are promising, and only continues down the viable branches.

```
                        Problem
                       /       \
                 Thought A    Thought B
                /    \           |
             A.1    A.2        B.1  ← dead end, backtrack
            (win!)   |
                   A.2.1
                  (dead end)
```

**How it differs from CoT:**
- CoT follows **one** reasoning path from start to finish
- ToT explores **multiple** paths simultaneously and can **backtrack** when a path fails
- ToT uses the model itself to **evaluate** whether each partial solution is promising

**When to use it:** Problems that require search, planning, or strategic lookahead — like puzzles, code debugging, or multi-step decision-making where early choices constrain later options.

> **Note:** ToT is more of a system design pattern than a single prompt. It typically requires orchestration code that manages the branching and evaluation loop.

---

### 2.4 ReAct (Reasoning + Acting)

ReAct (Yao et al., 2022) combines Chain-of-Thought reasoning with the ability to **take actions** — like searching the web, querying a database, or calling an API — and then **observe the results** before continuing to reason.

```
┌──────────────────────────────────────────────────────────┐
│                   ReAct LOOP                              │
│                                                          │
│  Thought  → "I need to find when Python was created"    │
│  Action   → Search("Python programming language year")  │
│  Observe  → "Python was first released in 1991..."      │
│  Thought  → "Now I need to find who created it"         │
│  Action   → Search("Python creator")                    │
│  Observe  → "Guido van Rossum..."                       │
│  Thought  → "I now have both facts. I can answer."      │
│  Answer   → "Python was created by Guido van Rossum     │
│              and first released in 1991."                │
└──────────────────────────────────────────────────────────┘
```

**Why it matters:** Pure CoT relies entirely on the model's training data — it cannot look things up. ReAct solves this by letting the model **ground its reasoning in external facts**, dramatically reducing hallucination.

**ReAct prompt structure:**
```text
Answer the following question using the Thought/Action/Observation pattern.

Available actions:
- Search[query]: Search for information
- Lookup[term]: Look up a specific term on the current page

Question: "What is the elevation range for the area that the
eastern sector of the Colorado orogeny extends into?"

Thought 1: I need to search for the Colorado orogeny and find
information about its eastern sector.
Action 1: Search["Colorado orogeny eastern sector"]
Observation 1: The Colorado orogeny extended into the High Plains...
Thought 2: Now I need to find the elevation range of the High Plains.
Action 2: Search["High Plains elevation range"]
Observation 2: The High Plains rise from around 1,800 ft to 7,000 ft.
Thought 3: I now have the answer.
Answer: The elevation range is approximately 1,800 to 7,000 feet.
```

> **Insight:** ReAct is the pattern behind most modern AI agents. When you see an LLM "searching the web" or "running code," it is using a ReAct-style loop. The agents we build in Part 2 of this document are ReAct made real — with actual tools the LLM can call.

---

### 2.5 Retrieval-Augmented Generation (RAG)

RAG is not strictly a prompting technique — it is an **architecture pattern** — but understanding it is essential because it changes how you write prompts.

```
┌─────────────┐    ┌────────────────┐    ┌─────────────────┐
│  User Query  │───►│  Retriever     │───►│  LLM Prompt     │
│              │    │  (search docs, │    │  = query         │
│  "What is    │    │   vector DB,   │    │  + retrieved     │
│   our refund │    │   knowledge    │    │    context       │
│   policy?"   │    │   base)        │    │  + instructions  │
└─────────────┘    └────────────────┘    └─────────────────┘
                          │                       │
                   Retrieved chunks          Final answer
                   from company docs       grounded in docs
```

**The core idea:** Instead of hoping the model knows the answer, you **retrieve relevant documents first** and **paste them into the prompt** as context. The model then generates an answer grounded in those documents.

**Why it matters:**
- Reduces hallucination (answers are grounded in real sources)
- Keeps the model current (no need to retrain when information changes)
- Works with private data (your company docs, your codebase, your notes)

**A RAG-style prompt:**
```text
Answer the user's question based ONLY on the provided context.
If the context does not contain enough information to answer,
say "I don't have enough information to answer this."

## Context
[Retrieved document chunks would be inserted here by the system]

## Question
What is the refund policy for enterprise customers?
```

> **Key takeaway:** RAG separates *what the model knows* from *what information it has access to*. This is the single most important pattern for building production LLM applications.

---

### Technique Comparison

| Technique | What It Does | Best For | Limitation |
|-----------|-------------|----------|------------|
| **CoT** | Step-by-step reasoning | Math, logic, analysis | Still uses only internal knowledge |
| **Self-Consistency** | Multiple CoT paths + vote | High-accuracy reasoning | Costs N times more (N paths) |
| **Tree of Thoughts** | Branching + backtracking | Search & planning problems | Complex to implement |
| **ReAct** | Reasoning + external actions | Fact-finding, tool use | Needs tool infrastructure |
| **RAG** | Retrieve context, then generate | Knowledge-grounded Q&A | Quality depends on retrieval |

---

## 3. Prompt Structure and Frameworks

A well-structured prompt is not a single sentence — it is an organized document with distinct sections. Two frameworks help you build prompts systematically: **PRISM** and **KERNEL**.

### 3.1 The Canonical Prompt Structure

```
┌─────────────────────────────────────────────────────────┐
│  ANATOMY OF AN EFFECTIVE PROMPT                         │
│                                                         │
│  ┌──────────┐  Who the model should act as              │
│  │  ROLE    │  "You are a senior data analyst"          │
│  ├──────────┤                                           │
│  │ CONTEXT  │  Background info the model needs          │
│  ├──────────┤                                           │
│  │  TASK    │  The specific action to perform            │
│  ├──────────┤                                           │
│  │CONSTRAINT│  Rules, limits, and boundaries            │
│  ├──────────┤                                           │
│  │  FORMAT  │  How the output should look               │
│  ├──────────┤                                           │
│  │ EXAMPLES │  Input-output pairs showing expected      │
│  └──────────┘  behavior                                 │
└─────────────────────────────────────────────────────────┘
```

Not every prompt needs all six sections. But when output quality matters, including more sections gives the model less room to guess — and guessing is where errors come from.

---

### 3.2 The PRISM Framework

PRISM stands for **Persona, Request, Information, Style, and Mode**. It is a practical checklist for building prompts.

| Component | Purpose | Example |
|-----------|---------|---------|
| **P**ersona | Who the model acts as | "You are a senior backend engineer" |
| **R**equest | What you want done | "Review this API endpoint for security issues" |
| **I**nformation | Context and data | The actual code, documentation, or background |
| **S**tyle | Tone and voice | "Be direct and technical. No pleasantries." |
| **M**ode | Output format | "Return a numbered list of issues with severity ratings" |

**Full PRISM example:**

````text
## Persona
You are a senior backend engineer specializing in API security.

## Request
Review the following REST API endpoint and identify security
vulnerabilities.

## Information
```python
@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    return jsonify(result.fetchone())
```

## Style
Be direct and technical. Prioritize severity. Do not sugarcoat issues.

## Mode
Return a numbered list. Each item should include:
- Vulnerability name
- Severity (Critical / High / Medium / Low)
- One-line explanation
- Fix recommendation
````

---

### 3.3 The KERNEL Framework

KERNEL stands for **Knowledge, Expectation, Role, Nuance, Examples, and Language**. It is more detailed than PRISM and suits complex or nuanced tasks.

| Component | Purpose |
|-----------|---------|
| **K**nowledge | Domain-specific facts the model needs |
| **E**xpectation | What success looks like (acceptance criteria) |
| **R**ole | The expert identity the model should adopt |
| **N**uance | Edge cases, exceptions, and subtleties |
| **E**xamples | Demonstrations of correct behavior |
| **L**anguage | Terminology, tone, register |

**Full KERNEL example:**

```text
## Knowledge
In the EU, GDPR Article 17 gives individuals the "right to erasure"
(right to be forgotten). This right is not absolute — it can be
overridden by legal obligations, public interest, or freedom of
expression.

## Expectation
Given a user's data deletion request, determine whether it qualifies
for erasure under GDPR Article 17. Return a structured decision with
reasoning.

## Role
You are a data privacy compliance officer at a European fintech company.

## Nuance
- Financial transaction records must be retained for 5 years under
  EU anti-money laundering regulations, even if the user requests
  deletion.
- Marketing consent data CAN be deleted immediately.
- Account identity data must be pseudonymized, not deleted, if
  transactions exist.

## Examples
Request: "Delete all my data. I closed my account 3 years ago."
Decision: PARTIAL ERASURE
Reasoning: Marketing and preference data can be deleted. Transaction
records must be retained for 2 more years (5-year AML requirement).
Identity data will be pseudonymized.

## Language
Use formal compliance language. Reference specific regulation articles
where relevant. Avoid legal jargon that a non-lawyer customer could
not understand.
```

---

### PRISM vs. KERNEL

| Use Case | Choose |
|----------|--------|
| Quick internal tool prompts | PRISM |
| Customer-facing or regulated output | KERNEL |
| Prototype / experimentation | PRISM |
| Complex domain with edge cases | KERNEL |

> **Insight:** These frameworks are checklists, not rigid templates. Use them to avoid forgetting important prompt components. Once you internalize the pattern, you will naturally include these elements without labeling them.

---

## 4. From Prompts to Agents — The Theory

In sections 1–3, we learned how to write effective prompts — single instructions that produce a single output. But what happens when a task is too complex for one prompt? What if the model needs to use tools, make decisions, and iterate?

That is where **agents** come in.

### 4.1 What Is an AI Agent?

An AI agent is a system where an LLM operates in a **loop**, deciding what to do next based on observations. Instead of one prompt in, one answer out — an agent can reason, take actions, observe results, and keep going until the task is done.

```
┌─────────────────────────────────────────────────────────────┐
│                     THE AI AGENT                             │
│                                                              │
│  ┌──────────┐                                                │
│  │   LLM    │ ◄── The "brain" - reasons about what to do    │
│  │  (Brain) │                                                │
│  └────┬─────┘                                                │
│       │                                                      │
│  ┌────▼─────┐                                                │
│  │  TOOLS   │ ◄── Functions the agent can call               │
│  │          │     (search, calculate, APIs, databases)       │
│  └────┬─────┘                                                │
│       │                                                      │
│  ┌────▼─────┐                                                │
│  │  MEMORY  │ ◄── Conversation history, session state        │
│  └────┬─────┘                                                │
│       │                                                      │
│  ┌────▼─────┐                                                │
│  │   LOOP   │ ◄── Observe → Think → Act → Repeat            │
│  └──────────┘                                                │
└─────────────────────────────────────────────────────────────┘
```

The four components:

| Component | What It Does | Example |
|-----------|-------------|---------|
| **LLM (Brain)** | Reasons about the task, decides next action | GPT-4o deciding to search the web before answering |
| **Tools** | Functions the agent can call to interact with the world | Rolling dice, querying a database, calling an API |
| **Memory** | Stores conversation history and state across turns | Remembering the user's name from 3 messages ago |
| **Loop** | The orchestration that keeps the agent running until done | Retrying a failed tool call, chaining multiple steps |

### 4.2 The ReAct Loop Revisited — Agents Are ReAct Made Real

In section 2.4, we covered ReAct as a prompting technique — a text pattern where the model writes "Thought → Action → Observation" on paper. An AI agent is what happens when you **actually wire up those actions to real code**.

```
┌──────────────────────────────────────────────────────────────┐
│         ReAct (Theory)          │    Agent (Practice)         │
│                                 │                             │
│  Thought: "I need the time"    │    LLM decides to call      │
│  Action: GetTime()              │    the get_time() function  │
│  Observation: "3:42 PM"         │    Runtime returns "3:42 PM"│
│  Thought: "Now I can answer"   │    LLM generates final reply│
│                                 │                             │
│  All text in the prompt         │    Real code execution      │
└──────────────────────────────────────────────────────────────┘
```

When you define a tool in PydanticAI and the LLM "calls" it, here is what actually happens:

1. The LLM generates a **tool call request** (structured JSON saying "call `roll_dice` with `sides=20`")
2. The agent framework **intercepts** this and runs the actual Python function
3. The function result is **fed back** to the LLM as an observation
4. The LLM decides whether to call another tool or return a final answer

This loop continues until the LLM decides it has enough information to respond.

### 4.3 Agent Architectures

Not all agent systems look the same. Here are the four core patterns:

**Pattern 1: Single Agent**

One LLM with tools. The simplest and most common pattern.

```
User → [ Agent + Tools ] → Response
```

Best for: most tasks. Start here. Only add complexity when a single agent can't handle the job.

**Pattern 2: Sequential Pipeline**

Multiple agents chained together, each handling one step. Output of agent A feeds into agent B.

```
User → [ Researcher ] → [ Writer ] → [ Editor ] → Response
```

Best for: multi-stage workflows where each stage requires a different skill or persona.

**Pattern 3: Delegation (Agent Calls Agent)**

One agent calls another agent as a tool. The outer agent decides when to delegate.

```
User → [ Writer Agent ]
              │
              ├── tool call → [ Research Agent ] → facts
              │
              └── uses facts to write final response
```

Best for: when one agent needs specialized sub-capabilities on demand.

**Pattern 4: Debate / Parallel**

Multiple agents work on the same problem independently, then a final agent synthesizes or judges.

```
User → ┬── [ Agent A ] ──┐
       └── [ Agent B ] ──┤──► [ Judge ] → Response
                          │
```

Best for: getting diverse perspectives, quality assurance, creative tasks.

### 4.4 When to Use Agents vs. Plain Prompts

| Situation | Use |
|-----------|-----|
| Single question, single answer | Plain prompt |
| Task requires external data (APIs, databases, files) | Agent with tools |
| Multi-step workflow with distinct stages | Agent pipeline |
| Task requires real-time information | Agent with search tools |
| Conversational context matters across turns | Agent with memory |
| You need structured, validated output | Agent with Pydantic output types |
| Task is simple and well-defined | Plain prompt (don't over-engineer) |

> **Key principle:** Start with the simplest approach that works. A well-written prompt is better than a poorly designed agent. Add agent capabilities only when a plain prompt genuinely can't handle the task.

---

## 5. Hands-On — Building Agents with PydanticAI

This section walks through 10 runnable Python examples, each teaching a specific agent concept. All files are in the project root and use **PydanticAI** — a type-safe, Pydantic-native agent framework that works with multiple LLM providers.

**Why PydanticAI:**
- Type-safe tool definitions and structured outputs via Pydantic models
- Built-in support for dependency injection, streaming, and multi-model setups
- Clean, minimal API — agents are just Python objects

### Setup

```bash
# Install dependencies
uv pip install -r requirements.txt

# Set your OpenAI API key
# Windows PowerShell:
$env:OPENAI_API_KEY = "your-key-here"

# Mac/Linux:
export OPENAI_API_KEY="your-key-here"
```

All examples use `openai:gpt-5-mini` as the model.

---

### 5.1 Hello World Agent — `01_basic_agent.py`

The simplest possible agent. Creates an agent, sends a message, prints the response. **This is your "it works" smoke test.**

**Concept taught:** Agent creation, `run_sync` for synchronous execution.

**Run it:**
```bash
python 01_basic_agent.py
```

**Key code:**
```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-5-mini', instructions='You are a helpful assistant.')
result = agent.run_sync('What are the three laws of robotics?')
print(result.output)
```

> **Try this:** Change the instructions to give the agent a different persona (e.g., "You are a pirate"). Run it again and see how the response changes. Same prompt, different instructions — that's the power of the system prompt.

---

### 5.2 Structured Output — `02_structured_output.py`

Agent that returns a **Pydantic model** instead of free-form text. The LLM's output is automatically validated against your schema — if it doesn't match, PydanticAI retries.

**Concept taught:** Structured output with `output_type`, Pydantic models as contracts.

**Run it:**
```bash
uvicorn 02_structured_output:app --reload
```

**Try it:**
```bash
curl -X POST http://localhost:8000/review ^
  -H "Content-Type: application/json" ^
  -d "{\"movie\": \"Inception\"}"
```

**What comes back:**
```json
{
  "title": "Inception",
  "rating": 9.0,
  "pros": ["Mind-bending concept", "Stellar cast", "Stunning visuals"],
  "cons": ["Can be confusing on first watch"],
  "one_liner": "A heist movie inside a dream inside a dream."
}
```

**Key insight:** The output is guaranteed to match your Pydantic schema. No parsing JSON from free text. No hoping the model remembered to include all fields. The framework enforces it.

---

### 5.3 Agent with Tools — `03_tools_agent.py`

An agent with three tools it can call: `roll_dice`, `get_time`, and `calculate`. The LLM **autonomously decides** which tools to use based on the user's question.

**Concept taught:** Tool registration with `@agent.tool_plain`, how the agent decides which tools to call.

**Run it:**
```bash
uvicorn 03_tools_agent:app --reload
```

**Try it:**
```bash
curl -X POST http://localhost:8000/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"What time is it, and roll me a d20\"}"
```

The agent will call **both** `get_time` and `roll_dice` — without you telling it which tools to use. It reads the question, matches it to available tools, and calls them.

> **Try this:** Ask it "What is 1337 * 42?" and watch it use the calculator tool. Then ask "Tell me a joke" — it won't call any tools, because none are relevant. The agent decides.

---

### 5.4 Dependencies and Dynamic Instructions — `04_deps_agent.py`

An agent that receives **runtime context** — the user's name and preferred response style — injected as dependencies. The system prompt changes dynamically based on who's asking.

**Concept taught:** Dependency injection with `deps_type`, dynamic instructions with `@agent.instructions`.

**Run it:**
```bash
uvicorn 04_deps_agent:app --reload
```

**Try it:**
```bash
curl -X POST http://localhost:8000/assist ^
  -H "Content-Type: application/json" ^
  -d "{\"user_name\": \"Abhi\", \"style\": \"pirate\", \"question\": \"What should I eat for lunch?\"}"
```

The agent answers as a pirate, addressing you by name. Change `"style"` to `"Shakespeare"` or `"sports commentator"` and the entire persona shifts — same agent, different deps.

**Why this matters:** In production, deps carry real context — the current user's permissions, their account data, feature flags. Dynamic instructions let a single agent serve many users with personalized behavior.

---

### 5.5 Streaming Responses — `05_streaming.py`

An agent that streams its response token by token, like a real chat interface. No waiting for the full response — text appears as it's generated.

**Concept taught:** `run_stream`, async generators, `StreamingResponse` in FastAPI.

**Run it:**
```bash
uvicorn 05_streaming:app --reload
```

**Try it (watch it stream in real time):**
```bash
curl http://localhost:8000/story?topic=dragons
```

---

### 5.6 Multi-Agent Debate Arena — `06_debate_arena.py`

**The showstopper demo.** Three agents — a passionate debater FOR, a cold logical debater AGAINST, and a formal judge — argue about any topic you give them.

**Concept taught:** Multi-agent systems, message passing between agents, agent personas.

**Run it:**
```bash
uvicorn 06_debate_arena:app --reload
```

**Try it:**
```bash
curl -X POST http://localhost:8000/debate ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\": \"Pineapple belongs on pizza\"}"
```

**What happens inside:**

```
┌──────────────────────────────────────────────────────────┐
│                    DEBATE FLOW                            │
│                                                          │
│  Round 1: Opening Arguments                              │
│  ┌─────────────┐           ┌──────────────────┐         │
│  │ Debater FOR  │           │ Debater AGAINST   │         │
│  │ (passionate) │           │ (cold, logical)   │         │
│  └──────┬──────┘           └────────┬─────────┘         │
│         │                           │                    │
│  Round 2: Rebuttals (each reads opponent's argument)    │
│  ┌──────▼──────┐           ┌────────▼─────────┐         │
│  │  Rebuttal   │           │    Rebuttal      │         │
│  └──────┬──────┘           └────────┬─────────┘         │
│         │                           │                    │
│         └───────────┬───────────────┘                    │
│                     ▼                                    │
│            ┌────────────────┐                            │
│            │     JUDGE      │                            │
│            │ Scores: Logic, │                            │
│            │ Persuasion,    │                            │
│            │ Evidence       │                            │
│            │ Declares winner│                            │
│            └────────────────┘                            │
└──────────────────────────────────────────────────────────┘
```

The response includes every argument, every rebuttal, and the judge's scored verdict. Try controversial topics for the most entertaining results.

---

### 5.7 Sequential Agent Pipeline — `07_agent_pipeline.py`

Three agents chained in sequence: **Researcher** (finds facts) -> **Writer** (drafts a blog post) -> **Editor** (polishes and titles it). Each agent's output feeds into the next.

**Concept taught:** Agent pipelines, output-as-input chaining, stage visibility.

**Run it:**
```bash
uvicorn 07_agent_pipeline:app --reload
```

**Try it:**
```bash
curl -X POST http://localhost:8000/blog ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\": \"quantum computing\"}"
```

The response shows all three stages — the raw facts, the draft, and the polished final version — so you can see exactly how each agent transformed the content.

---

### 5.8 Code Roaster — `08_roast_my_code.py`

An agent with the persona of a brutally honest senior engineer who roasts your code like Gordon Ramsay roasts food. It finds **real issues** (bugs, bad practices, security problems) but delivers the feedback with dramatic flair.

**Concept taught:** Persona-driven agents, structured output, combining entertainment with utility.

**Run it:**
```bash
uvicorn 08_roast_my_code:app --reload
```

**Try it:**
```bash
curl -X POST http://localhost:8000/roast ^
  -H "Content-Type: application/json" ^
  -d "{\"code\": \"import pickle; data = pickle.loads(user_input)\"}"
```

Returns structured output: the roast text, a score (1-10), a list of actual issues found, and one genuine compliment. Try submitting your own code.

---

### 5.9 Audio Transcription + Analysis — `09_whisper_agent.py`

A two-step pipeline: first transcribes audio using OpenAI's Whisper API, then passes the transcript to a PydanticAI agent that extracts a summary, action items, and sentiment.

**Concept taught:** Combining traditional APIs with agents, real-world multi-modal pipelines.

**Run it:**
```bash
uvicorn 09_whisper_agent:app --reload
```

**Try it:**
```bash
curl -X POST http://localhost:8000/transcribe -F "file=@recording.mp3"
```

Returns the raw transcript plus structured analysis. This pattern — traditional API + agent analysis — is extremely common in production systems.

---

### 5.10 Conversation Memory — `10_memory_chat.py`

A chat agent that **remembers previous messages** within a session. Uses PydanticAI's `message_history` parameter with an in-memory session store.

**Concept taught:** Stateful agents, conversation history, session management.

**Run it:**
```bash
uvicorn 10_memory_chat:app --reload
```

**Try it (two requests, same session):**
```bash
curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\": \"abc\", \"message\": \"My name is Abhi\"}"

curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\": \"abc\", \"message\": \"What is my name?\"}"
```

The second response will correctly say "Abhi" because the agent has access to the conversation history for that session. Change the `session_id` and it starts fresh — separate sessions, separate memories.

**View history:**
```bash
curl http://localhost:8000/history/abc
```

---

## 6. Quick Reference — Agent Patterns

### Pattern-to-File Map

| Pattern | File | What It Demonstrates |
|---------|------|---------------------|
| Basic agent | `01_basic_agent.py` | Minimal agent, `run_sync` |
| Structured output | `02_structured_output.py` | Pydantic models as output types |
| Tool use | `03_tools_agent.py` | Agent autonomously picks tools |
| Dependencies | `04_deps_agent.py` | Runtime context injection |
| Streaming | `05_streaming.py` | Token-by-token response delivery |
| Multi-agent debate | `06_debate_arena.py` | Multiple agents + message passing |
| Pipeline | `07_agent_pipeline.py` | Sequential agent chaining |
| Persona + fun | `08_roast_my_code.py` | Character-driven structured output |
| API + agent | `09_whisper_agent.py` | Traditional API feeding into agent |
| Memory | `10_memory_chat.py` | Stateful conversation across requests |

### Mental Models for Agents

**Mental Model 1: Agents are loops, not lines.**

A prompt is a straight line: input -> output. An agent is a loop: input -> think -> act -> observe -> think -> act -> ... -> output. The agent keeps going until it decides it's done.

**Mental Model 2: Tools are the agent's hands.**

Without tools, an LLM can only think. With tools, it can *do*. A tool is just a Python function the agent is allowed to call. The agent reads the function's name and docstring to understand what it does.

**Mental Model 3: Start simple, add complexity only when needed.**

Don't build a multi-agent pipeline when a single agent with one tool would work. The debug surface area of a 3-agent system is 3x that of a single agent. Earn complexity by proving the simpler approach fails first.

**Mental Model 4: The instructions are everything.**

Two agents with the same model and the same tools but different instructions will behave completely differently. The debate arena proves this — same GPT-4o, same tools (none), wildly different outputs because of different personas in the instructions.

**Mental Model 5: Structured output is your best friend.**

Free-form text is great for humans. Structured output (Pydantic models) is great for code. If your agent's output needs to be consumed by another system — another agent, a frontend, a database — use structured output. Always.

---

### Running Everything

```bash
# Install all dependencies
uv pip install -r requirements.txt

# Run any standalone script
python 01_basic_agent.py

# Run any FastAPI server
uvicorn 02_structured_output:app --reload
uvicorn 03_tools_agent:app --reload
uvicorn 04_deps_agent:app --reload
uvicorn 05_streaming:app --reload
uvicorn 06_debate_arena:app --reload
uvicorn 07_agent_pipeline:app --reload
uvicorn 08_roast_my_code:app --reload
uvicorn 09_whisper_agent:app --reload
uvicorn 10_memory_chat:app --reload
```

> **Note:** Each server runs on port 8000 by default. Only run one at a time, or specify different ports with `--port 8001`.

---

*This document is part of the LLM Bootcamp curriculum. Part 1 covers prompt engineering theory. Part 2 covers hands-on agent development. All code examples are designed to be run live.*
