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
- Collects tools and tool rules via entry points.
- Provides helpers to inspect provider tools and settings.
- Resolves string model names via `kantan_llm.get_llm`.
- Injects AsyncOpenAI clients via AsyncClientBundle/KantanAsyncLLM.

## Quick Start

```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = agent.run("Hello")
print(context["result"].final_output)
```

Async usage
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = await agent.run_async("Hello")
print(context["result"].final_output)
```

Model selection
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.", model="gpt-5-mini")
context = agent.run("Hello")
print(context["result"].final_output)
```

AsyncClientBundle
```python
from kantan_llm import get_async_llm_client
from kantan_agents import Agent

bundle = get_async_llm_client("gpt-5-mini")
agent = Agent(name="basic-agent", instructions="You are a helpful assistant.", model=bundle)
context = agent.run("Hello")
print(context["result"].final_output)
```

## Docs

- `docs/concept.md`
- `docs/spec.md`
- `docs/architecture.md`
- `docs/plan.md`
- `docs/tutorial.md`
- `docs/usage.md`
