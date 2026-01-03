kantan-agents Tutorial Unit 8 (v0.1)

Title

Tool-based evaluation and prompt analysis

Overview

This unit combines a tool call with rubric output. The rubric is saved into traces to support evaluation workflows. This is useful when comparing prompt variants or tracking quality over time.

Step

- Define a tool function.
- Set output_type=RUBRIC.
- Run and read rubric output from final_output.

How to

- Use tools for deterministic checks.
- RUBRIC maps to structured output that is also stored in trace spans.

Code
```python
from kantan_agents import Agent, PolicyMode, RUBRIC, get_context_with_policy


def word_count(text: str) -> int:
    return len(text.split())

agent = Agent(
    name="evaluator",
    instructions="Use word_count and then output a rubric with score and comments.",
    tools=[word_count],
    output_type=RUBRIC,
)
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = agent.run("Assess this sentence: 'Tracing enables analysis.'", context)
print(context["result"].final_output)
```
