kantan-agents Tutorial Unit 9 (v0.1)

Title

Provide tools via entry points

Overview

This unit shows how external packages can provide tools and tool rules. Providers are discovered via project.entry-points, so users do not need to wire tools manually. This is the recommended way to ship shared tool sets. Skip if you are not distributing tools.

Step

- Register a provider class in project.entry-points.
- Implement list_tools and get_tool_rules.
- Install the package so entry points can be discovered.

How to

- Use the group name "kantan_agents.tools".
- Return tools with a stable name attribute.
- Consumers can use get_context_with_tool_rules(ToolRulesMode.RECOMMENDED) to load provider tool rules.
- Override by updating context["tool_rules"] before running.
- For a provider template and tool_rules.params examples, see `docs/tool_provider_guide.md`.

Code
```toml
[project.entry-points."kantan_agents.tools"]
my_tools = "my_package.tools:MyToolProvider"
```

```python
class MyToolProvider:
    def list_tools(self):
        return [my_tool_function]

    def get_tool_rules(self):
        return {
            "allow": ["my_tool_function"],
            "deny": [],
            "params": {"my_tool_function": {"text": {"type": "string", "maxLength": 200}}},
        }
```
