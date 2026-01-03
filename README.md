# kantan-agents

kantan-agents is a thin, opinionated wrapper around the OpenAI Agents SDK that makes observability and evaluation "just happen" by default.

## What it does

- Re-exports the Agents SDK tracing API.
- Provides an Agent wrapper that injects standardized Trace metadata.
- Provides a minimal Prompt model for versioned instructions.
- Injects Prompt metadata into Trace metadata when Prompt is used.
- Stores recent input/output pairs in context history.
- Supports output_dest to store structured output under a custom context key.
- Supports structured outputs via `output_type` and a `RUBRIC` schema helper.
- Supports handoffs between Agent instances.

## Quick Start

```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = agent.run("Hello", {})
print(context["result"].final_output)
```

## Docs

- `docs/concept.md`
- `docs/spec.md`
- `docs/architecture.md`
- `docs/plan.md`
- `docs/tutorial.md`
- `docs/usage.md`
