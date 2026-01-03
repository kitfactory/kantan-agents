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
Create an Agent and call `run`. The return type is a context dict.

Code:
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = agent.run("Hello")
print(context["result"].final_output)
```

Unit 2: Use context for templated instructions

Use Case:
Inject runtime variables into the instruction template.

Approach:
Use `{{ }}` placeholders with `$ctx` and pass `context` to `run`.

Code:
```python
from kantan_agents import Agent

agent = Agent(
    name="templated-agent",
    instructions="Summarize {{ $ctx.topic }} in {{ $ctx.style }}.",
)
context = agent.run(
    "Use concise bullet points.",
    context={"topic": "trace metadata", "style": "two sentences"},
)
print(context["result"].final_output)
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
context = agent.run("Explain trace metadata in one sentence.")
print(context["result"].final_output)
```

Unit 4: Apply policy to tool usage

Use Case:
Allow only specific tools and constrain their parameters.

Approach:
Provide a policy in the context and let the Agent enforce it at tool call time.

Code:
```python
from kantan_agents import Agent


def word_count(text: str) -> int:
    return len(text.split())


agent = Agent(
    name="policy-agent",
    instructions="Use word_count and answer briefly.",
    tools=[word_count],
)
policy = {
    "allow": ["word_count"],
    "deny": [],
    "params": {"word_count": {"text": {"type": "string", "maxLength": 200}}},
}
context = agent.run("Count the words in this sentence.", context={"policy": policy})
print(context["result"].final_output)
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
context = agent.run("Explain tracing in one sentence.")
print(context["result"].final_output)
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
context = agent.run("Summarize the release notes.")
print(context["result"].final_output)
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
context = manager.run("I need a refund for last week's order.")
print(context["result"].final_output)
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
context = agent.run("Assess this sentence: 'Tracing enables analysis.'")
print(context["result"].final_output)
```

Unit 9: Provide tools via entry points

Use Case:
Load tools and policy from external packages without manual wiring.

Approach:
Expose a provider in `project.entry-points."kantan_agents.tools"` and return tools/policy.

Code:
```toml
[project.entry-points."kantan_agents.tools"]
my_tools = "my_package.tools:MyToolProvider"
```

```python
class MyToolProvider:
    def list_tools(self):
        return [my_tool_function]

    def get_policy(self):
        return {
            "allow": ["my_tool_function"],
            "deny": [],
            "params": {"my_tool_function": {"text": {"type": "string", "maxLength": 200}}},
        }
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
