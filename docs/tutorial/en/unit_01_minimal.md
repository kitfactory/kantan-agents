kantan-agents Tutorial Unit 1 (v0.1)

Title

Run a minimal Agent

Overview

This unit shows the smallest runnable example. You will create a single Agent, call run, and read the SDK result from the returned context. We will cover context details in the next unit.

Step

- Create an Agent with a short instruction string.
- Call run (omit context).
- Read context["result"].

How to

- If you omit context, kantan-agents creates an empty dict automatically.
- The returned context always contains a result after run completes.
- History is stored in context["history"] when enabled.
- If you pass a string model name, kantan-llm resolves it via get_llm.
- If you pass AsyncClientBundle/KantanAsyncLLM, kantan-agents injects the AsyncOpenAI client.

Common pitfalls

- Not keeping the returned context for later access
- Printing context itself instead of context["result"]

Code
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = agent.run("Hello")
print(context["result"].final_output)
```

With a model name
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.", model="gpt-5-mini")
context = agent.run("Hello")
print(context["result"].final_output)
```
