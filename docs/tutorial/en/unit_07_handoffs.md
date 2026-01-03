kantan-agents Tutorial Unit 7 (v0.1)

Title

Delegate with handoffs

Overview

This unit demonstrates how a manager agent can hand work off to specialists. You build multiple Agent instances and pass them in handoffs. The SDK decides when to delegate based on instructions.

Step

- Create specialist agents.
- Create a manager agent with handoffs.
- Run through the manager to trigger delegation.

How to

- Keep instructions specific for each specialist.
- Pass the specialist Agent instances in a list.

Code
```python
from kantan_agents import Agent, PolicyMode, get_context_with_policy

booking_agent = Agent(name="booking", instructions="Handle booking tasks.")
refund_agent = Agent(name="refund", instructions="Handle refund tasks.")

manager = Agent(
    name="manager",
    instructions="Route tasks to specialists.",
    handoffs=[booking_agent, refund_agent],
)
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = manager.run("I need a refund for last week's order.", context)
print(context["result"].final_output)
```
