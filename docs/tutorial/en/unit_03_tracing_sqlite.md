kantan-agents Tutorial Unit 3 (v0.1)

Title

Enable tracing and persist records

Overview

This unit records traces to a local SQLite file. The tracer captures spans and metadata so you can inspect them later. Keep the tracer setup once per process and reuse it across runs.

Step

- Create a SQLiteTracer with a file path.
- Register it with set_trace_processors.
- Run an Agent so traces are written.

How to

- Use SQLiteTracer from kantan-llm.
- Reuse the same tracer instance for multiple runs.

Code
```python
from kantan_llm.tracing import SQLiteTracer
from kantan_agents import Agent, ToolRulesMode, get_context_with_tool_rules, set_trace_processors

tracer = SQLiteTracer("kantan_agents_traces.sqlite3")
set_trace_processors([tracer])

agent = Agent(name="trace-agent", instructions="Answer briefly.")
context = get_context_with_tool_rules(ToolRulesMode.RECOMMENDED)
context = agent.run("Explain trace metadata in one sentence.", context)
print(context["result"].final_output)
```
