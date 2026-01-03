kantan-agents Tutorial Unit 8 (v0.1)

Title

Tool-based evaluation and prompt analysis

Overview

This unit generates an answer and then evaluates it with a rubric prompt. This is the LLM-as-a-judge pattern, and the rubric is saved into traces to support evaluation workflows. This is useful when comparing prompt variants or tracking quality over time.

Step

- Generate an answer with a Prompt.
- Evaluate it with a rubric Prompt.
- Read the rubric output.

How to

- Split generation and evaluation into separate Agents.
- Use output_type=RUBRIC for the evaluation Agent.

Code
```python
from kantan_agents import Agent, PolicyMode, Prompt, RUBRIC, get_context_with_policy

generator_prompt = Prompt(
    name="A",
    version="v1",
    text="Write a short, clear explanation of trace metadata in one sentence.",
)
generator = Agent(name="generator", instructions=generator_prompt)

context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = generator.run("Explain trace metadata.", context)
generated = context["result"].final_output

judge_prompt = Prompt(
    name="A-judge",
    version="v1",
    text="Evaluate the answer and output a rubric with score (0-1) and comments.",
)
judge = Agent(name="judge", instructions=judge_prompt, output_type=RUBRIC)
judge_context = get_context_with_policy(PolicyMode.RECOMMENDED)
judge_context = judge.run(str(generated), judge_context)
print(judge_context["result"].final_output)
```
