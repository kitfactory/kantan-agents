kantan-agents Tutorial Unit 2 (v0.1)

Title

Use context for templated instructions

Overview

This unit explains how to inject runtime values into instructions. Templates use {{ $ctx.key }} so you can keep prompts clean while customizing behavior per run. Missing keys resolve to an empty string, so define only what you need.

Step

- Add $ctx placeholders to the instruction text.
- Build or extend a context with the variables you need.
- Call run with that context so the template can render.

How to

- Context is optional, but you must pass values when using templates.
- Reference variables as {{ $ctx.key }} in instructions.
- Update the context dict before calling run.
- You can reference history as {{ $ctx.history }} if you need it.

Common pitfalls

- Writing {{ key }} instead of {{ $ctx.key }}
- Forgetting to update context and getting empty strings

Code
```python
from kantan_agents import Agent, PolicyMode, get_context_with_policy

agent = Agent(
    name="templated-agent",
    instructions="Summarize {{ $ctx.topic }} in {{ $ctx.style }}.",
)
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context.update({"topic": "trace metadata", "style": "two sentences"})
context = agent.run("Use concise bullet points.", context)
print(context["result"].final_output)
```

History in templates example
```python
from kantan_agents import Agent, PolicyMode, get_context_with_policy

agent = Agent(
    name="history-agent",
    instructions="Summarize the last exchanges: {{ $ctx.history }}",
)
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = agent.run("First message", context)
context = agent.run("Second message", context)
print(context["history"])
```
