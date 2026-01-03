kantan-agents Tutorial Unit 9 (v0.1)

Title

Provide tools via entry points

Overview

This unit shows how external packages can provide tools and policy. Providers are discovered via project.entry-points, so users do not need to wire tools manually. This is the recommended way to ship shared tool sets. Skip if you are not distributing tools.

Step

- Register a provider class in project.entry-points.
- Implement list_tools and get_policy.
- Install the package so entry points can be discovered.

How to

- Use the group name "kantan_agents.tools".
- Return tools with a stable name attribute.

Code
```toml
[project.entry-points."kantan_agents.tools"]
my_tools = "my_package.tools:MyToolProvider"
```

```python
class MyToolProvider:
    def list_tools(self):
        return [my_tool_function]

    def get_policy(self):
        return {
            "allow": ["my_tool_function"],
            "deny": [],
            "params": {"my_tool_function": {"text": {"type": "string", "maxLength": 200}}},
        }
```
