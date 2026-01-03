kantan-agents Tutorial Unit 1 (v0.1)

Title

Run a minimal Agent

Overview

This unit shows the smallest runnable example. You will create a single Agent, call run, and read the SDK result from context. Keep this pattern in mind because every other unit builds on it.

Step

- Create an Agent with a short instruction string.
- Prepare a context (recommended policy is fine).
- Call run and read context["result"].

How to

- Use get_context_with_policy(PolicyMode.RECOMMENDED) as a safe default.
- The returned context always contains a result after run completes.
- History is stored in context["history"] when enabled.

Code
```python
from kantan_agents import Agent, PolicyMode, get_context_with_policy

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = agent.run("Hello", context)
print(context["result"].final_output)
```
