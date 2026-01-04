kantan-agents Tutorial Unit 5 (v0.1)

Title

Use Prompt with versioned instructions

Overview

This unit introduces the Prompt type for versioned instructions. Prompt metadata is injected into trace metadata automatically, which helps analysis and comparison across versions.
The metadata is stored on the Trace record (not on spans).

Step

- Create a Prompt with name, version, and text.
- Pass it as the Agent instructions.
- Run and inspect the result as usual.

How to

- Use Prompt.meta to add simple scalar metadata.
- Prompt.id is auto-generated when not provided.

Code
```python
from kantan_agents import Agent, ToolRulesMode, Prompt, get_context_with_tool_rules

prompt = Prompt(
    name="qa",
    version="v1",
    text="Answer the user briefly.",
    meta={"variant": "A"},
)

agent = Agent(name="prompted-agent", instructions=prompt)
context = get_context_with_tool_rules(ToolRulesMode.RECOMMENDED)
context = agent.run("Explain tracing in one sentence.", context)
print(context["result"].final_output)
```
