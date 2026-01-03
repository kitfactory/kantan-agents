kantan-agents Tutorial Unit 10 (v0.1)

Title

Search traces with kantan-llm

Overview

This unit records Prompt metadata and a rubric evaluation, then queries traces by Prompt metadata. You will also pull rubric results from the matching trace.

Step

- Run an Agent with a Prompt so metadata is recorded.
- Use output_type=RUBRIC to generate an evaluation.
- Query traces using prompt_name/prompt_version metadata.
- Fetch rubric data for the matching trace.

How to

- Prompt name/version are stored in Trace metadata.
- Use TraceQuery(metadata=...) for metadata filters.
- Use get_spans_by_trace to pull rubric data from spans.

Code
```python
from kantan_agents import Agent, PolicyMode, Prompt, RUBRIC, get_context_with_policy
from kantan_llm.tracing import SQLiteTracer, TraceQuery

tracer = SQLiteTracer("kantan_agents_traces.sqlite3")

prompt = Prompt(
    name="qa",
    version="v1",
    text="Answer the user briefly.",
    meta={"variant": "A"},
)
agent = Agent(
    name="prompted-agent",
    instructions=prompt,
    output_type=RUBRIC,
)
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = agent.run("Explain tracing in one sentence.", context)
print(context["result"].final_output)

traces = tracer.search_traces(query=TraceQuery(metadata={"prompt_name": "qa", "prompt_version": "v1"}))
for trace in traces:
    spans = tracer.get_spans_by_trace(trace.trace_id)
    rubrics = [span.rubric for span in spans if span.rubric]
    print(trace.trace_id, trace.metadata, rubrics)
```
