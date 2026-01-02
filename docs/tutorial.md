kantan-agents Tutorial (v0.1)

This tutorial is divided into units. Each unit follows the order: Use Case → Approach → Code.
The final unit shows tool-based evaluation and prompt analysis.

Prerequisites

- `OPENAI_API_KEY` is set in the environment
- Use `gpt-5-mini` for testing/verification

Unit 1: Run a minimal Agent

Use Case:
Confirm that a basic Agent run works end-to-end.

Approach:
Create an Agent and call `run`. The return type matches the Agents SDK.

Code:
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
result = agent.run("Hello")
print(result.final_output)
```

Unit 2: Use render_vars for templated instructions

Use Case:
Inject runtime variables into the instruction template.

Approach:
Use `{{ }}` placeholders in instructions and pass `render_vars` to `run`.

Code:
```python
from kantan_agents import Agent

agent = Agent(
    name="templated-agent",
    instructions="Summarize {{ topic }} in {{ style }}.",
)
result = agent.run(
    "Use concise bullet points.",
    render_vars={"topic": "trace metadata", "style": "two sentences"},
)
print(result.final_output)
```

Unit 3: Enable tracing and persist records

Use Case:
Save Trace data to SQLite for later analysis.

Approach:
Register `SQLiteTracer` from kantan-llm and then run the Agent.

Code:
```python
from kantan_llm.tracing import SQLiteTracer
from kantan_agents import Agent, set_trace_processors

tracer = SQLiteTracer("kantan_agents_traces.sqlite3")
set_trace_processors([tracer])

agent = Agent(name="trace-agent", instructions="Answer briefly.")
result = agent.run("Explain trace metadata in one sentence.")
print(result.final_output)
```

Unit 4: Add custom trace metadata via re-exported tracing API

Use Case:
Attach custom keys (e.g., session identifiers) to Trace metadata.

Approach:
Use the re-exported tracing API from `kantan_agents` and pass `trace_metadata` at run time.

Code:
```python
from kantan_llm.tracing import SQLiteTracer
from kantan_agents import Agent, set_trace_processors

tracer = SQLiteTracer("kantan_agents_traces.sqlite3")
set_trace_processors([tracer])

agent = Agent(name="trace-agent", instructions="Answer briefly.")
result = agent.run(
    "Explain trace metadata in one sentence.",
    trace_metadata={"session_id": "sess-001", "user_tier": "pro"},
)
print(result.final_output)
```

Unit 5: Use Prompt with versioned instructions

Use Case:
Persist prompt name/version in Trace metadata for analysis.

Approach:
Create a Prompt and pass it to the Agent. Standard metadata is auto-injected.

Code:
```python
from kantan_agents import Agent, Prompt

prompt = Prompt(
    name="qa",
    version="v1",
    text="Answer the user briefly.",
    meta={"variant": "A"},
)

agent = Agent(name="prompted-agent", instructions=prompt)
result = agent.run("Explain tracing in one sentence.")
print(result.final_output)
```

Unit 6: Use structured output

Use Case:
Return a structured result for easier downstream analysis.

Approach:
Provide a Pydantic model via `output_type`.

Code:
```python
from pydantic import BaseModel
from kantan_agents import Agent

class Summary(BaseModel):
    title: str
    bullets: list[str]

agent = Agent(
    name="structured-agent",
    instructions="Summarize the input.",
    output_type=Summary,
)
result = agent.run("Summarize the release notes.")
print(result.final_output)
```

Unit 7: Delegate with handoffs

Use Case:
Split work into specialist agents and hand off conversations.

Approach:
Pass other Agent instances via `handoffs`.

Code:
```python
from kantan_agents import Agent

booking_agent = Agent(name="booking", instructions="Handle booking tasks.")
refund_agent = Agent(name="refund", instructions="Handle refund tasks.")

manager = Agent(
    name="manager",
    instructions="Route tasks to specialists.",
    handoffs=[booking_agent, refund_agent],
)
result = manager.run("I need a refund for last week's order.")
print(result.final_output)
```

Unit 8: Tool-based evaluation and prompt analysis

Use Case:
Record tool calls and rubric evaluations in Trace to support prompt analysis.

Approach:
Pass tools as callables and set `output_type=RUBRIC`.

Code:
```python
from kantan_agents import Agent, RUBRIC


def word_count(text: str) -> int:
    return len(text.split())

agent = Agent(
    name="evaluator",
    instructions="Use word_count and then output a rubric with score and comments.",
    tools=[word_count],
    output_type=RUBRIC,
)
result = agent.run("Assess this sentence: 'Tracing enables analysis.'")
print(result.final_output)
```

Using kantan-llm Search Service

- Use TraceSearchService to query spans and inspect structured output and rubric data.

```python
from kantan_llm.tracing import SQLiteTracer, SpanQuery

tracer = SQLiteTracer("kantan_agents_traces.sqlite3")
spans = tracer.search_spans(query=SpanQuery(limit=10))

for span in spans:
    print(span.span_type, span.output_kind, span.structured, span.rubric)
```
