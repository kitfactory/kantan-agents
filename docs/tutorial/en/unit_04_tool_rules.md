kantan-agents Tutorial Unit 4 (v0.1)

Title

Apply tool rules to tool usage

Overview

This unit shows how to constrain tool usage with tool rules. You can explicitly allow tools, deny tools, and add parameter constraints. Deny wins if a tool appears in both allow and deny. Skip this unit unless you need tool controls.

Step

- Define a tool function and attach it to the Agent.
- Build tool rules with allow/deny/params.
- Put tool rules into the context and run.

How to

- allow/deny can be lists or "*".
- params uses a small JSON Schema subset like type and maxLength.

Code
```python
from kantan_agents import Agent, ToolRulesMode, get_context_with_tool_rules


def word_count(text: str) -> int:
    return len(text.split())


agent = Agent(
    name="tools-agent",
    instructions="Use word_count and answer briefly.",
    tools=[word_count],
)
tool_rules = {
    "allow": ["word_count"],
    "deny": [],
    "params": {"word_count": {"text": {"type": "string", "maxLength": 200}}},
}
context = get_context_with_tool_rules(ToolRulesMode.RECOMMENDED)
context["tool_rules"] = tool_rules
context = agent.run("Count the words in this sentence.", context)
print(context["result"].final_output)
```
