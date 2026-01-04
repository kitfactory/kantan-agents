kantan-agents Tutorial Unit 6 (v0.1)

Title

Use structured output

Overview

This unit returns typed output using a Pydantic model. Structured output makes downstream processing easier and avoids parsing free-form text. The final_output is an instance of your model.

Step

- Define a Pydantic model.
- Pass it as output_type to the Agent.
- Set output_dest to store structured output in context.
- Run and read final_output as a model instance.

How to

- Use model fields to validate the response.
- Access values directly on the returned model.
- output_dest stores a dict version in context.
- output_dest overwrites existing keys and is skipped when output is not dict-like.
- Use descriptive keys such as summary_json or evaluation_rubric.

Code
```python
from pydantic import BaseModel
from kantan_agents import Agent, ToolRulesMode, get_context_with_tool_rules

class Summary(BaseModel):
    title: str
    bullets: list[str]

agent = Agent(
    name="structured-agent",
    instructions="Summarize the input.",
    output_type=Summary,
    output_dest="summary_json",
)
context = get_context_with_tool_rules(ToolRulesMode.RECOMMENDED)
context = agent.run("Summarize the release notes.", context)
print(context["result"].final_output)
print(context["summary_json"]["title"])
```
