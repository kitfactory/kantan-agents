# kantan-agents

kantan-agents is a thin, opinionated wrapper around the OpenAI Agents SDK that makes observability and evaluation "just happen" by default.

## What it does

- 🚀 Broad model support: switch providers/models by changing a single name, without rewriting Agent code.
- 🔍 Automatic trace metadata: observability and search are ready out of the box.
- 🧪 Prompt version tracking: keep prompt versions and metadata attached to every run.
- 📦 Context-first outputs: store structured output and history for easy reuse.
- 🤝 Tools + multi-agent handoffs: control tool usage with tool_rules and delegate safely.

## Kantan Stack (direction)

Kantan Stack aims to turn “build → run → observe/evaluate → improve” into a single, simple path.
OpenAI Agents SDK powers execution under the hood, but the recommended surface area is just
`kantan-llm` + `kantan-agents`.

- `kantan-agents`: runtime wrapper with standardized trace metadata (this repo).
- `kantan-llm`: model resolution + tracing backbone (dependency).
- `kantan-tools` (planned): installable tool packs with clear schemas/permissions.
- `kantan-lab` (planned): trace/prompt analysis, evals, and regression detection.

## Recommended path (Kantan-first)

1. Start with `Agent` + `Prompt` for versioned instructions.
2. Switch models by name without changing Agent code.
3. Enable tracing early (SQLite or your tracer of choice).
4. Add tools via entry points and control them with `tool_rules`.
5. Use structured output (and `RUBRIC`) to evaluate and iterate.

## Escape hatches (when you must)

- Using the Agents SDK directly is an escape hatch; prefer `kantan-llm` + `kantan-agents`.
- Async usage is an escape hatch for ASGI; use it only when you must avoid blocking an event loop.
- If you use the Agents SDK directly, keep prompt versions and trace metadata consistent.
- Swap tracing processors to route data to your preferred backend.

## Quick Start

```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = agent.run("Hello")
print(context["result"].final_output)
```

Model selection
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.", model="gpt-5-mini")
context = agent.run("Hello")
print(context["result"].final_output)
```

Tracing (SQLite)
```python
from kantan_agents import Agent, set_trace_processors
from kantan_llm.tracing import SQLiteTracer

tracer = SQLiteTracer("traces.sqlite3")
set_trace_processors([tracer])

agent = Agent(name="trace-agent", instructions="Answer briefly.")
context = agent.run("Why does tracing help?")
print(context["result"].final_output)
```

AsyncClientBundle (escape hatch)
```python
from kantan_llm import get_async_llm_client
from kantan_agents import Agent

bundle = get_async_llm_client("gpt-5-mini")
agent = Agent(name="basic-agent", instructions="You are a helpful assistant.", model=bundle)
context = agent.run("Hello")
print(context["result"].final_output)
```

Async usage (escape hatch)
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = await agent.run_async("Hello")
print(context["result"].final_output)
```

## Mini Tutorial (friendly tour)

Think of `context` as a backpack your Agent carries. Each run drops a fresh result in
`context["result"]`, and you can stash structured output or history alongside it.

### Step 1: Give your Agent a name tag (Prompt + metadata)
```python
from kantan_agents import Agent, Prompt

prompt = Prompt(
    name="qa",
    version="v1",
    text="Answer in one short sentence.",
    meta={"tone": "friendly"},
)

agent = Agent(name="support-agent", instructions=prompt)
context = agent.run("What is trace metadata?")
print(context["result"].final_output)
```
This keeps your prompt version and metadata attached to every trace.

### Step 2: Switch models with one line
```python
from kantan_agents import Agent

agent = Agent(name="switcher", instructions="Answer in one sentence.", model="gpt-5-mini")
context = agent.run("Why does model switching matter?")
print(context["result"].final_output)
```

### Step 3: Turn on tracing (SQLite)
```python
from kantan_agents import set_trace_processors
from kantan_llm.tracing import SQLiteTracer

tracer = SQLiteTracer("traces.sqlite3")
set_trace_processors([tracer])
```
Now your runs write traces. You can read them with plain SQLite:
```python
import sqlite3

conn = sqlite3.connect("traces.sqlite3")
conn.row_factory = sqlite3.Row
row = conn.execute(
    "SELECT id, metadata_json FROM traces ORDER BY id DESC LIMIT 1"
).fetchone()
print(dict(row))
```

### Step 4: Ask for structured output (and keep it)
```python
from pydantic import BaseModel
from kantan_agents import Agent

class Summary(BaseModel):
    title: str
    bullets: list[str]

agent = Agent(
    name="summarizer",
    instructions="Summarize in a title and 2 bullets.",
    output_type=Summary,
    output_dest="summary_json",
)

context = agent.run("Explain why tracing helps teams.")
print(context["summary_json"]["title"])
```

### Step 5: Async in ASGI (client injection)
Use `get_async_llm_client()` to inject an AsyncOpenAI client into Agents SDK:
```python
from kantan_llm import get_async_llm_client
from kantan_agents import Agent

bundle = get_async_llm_client("gpt-5-mini")
agent = Agent(name="async-agent", instructions="Say hi.", model=bundle)
context = await agent.run_async("Hello")
print(context["result"].final_output)
```

## Docs

- `docs/concept.md`
- `docs/spec.md`
- `docs/architecture.md`
- `docs/plan.md`
- `docs/tutorial.md`
- `docs/usage.md`
