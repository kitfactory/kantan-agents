from __future__ import annotations

import importlib.metadata

from .tool_rules import merge_tool_rules


def collect_tool_providers() -> tuple[list, dict | None]:
    tools: list = []
    rules: dict | None = None
    entry_points = importlib.metadata.entry_points()
    if hasattr(entry_points, "select"):
        candidates = entry_points.select(group="kantan_agents.tools")
    else:
        candidates = entry_points.get("kantan_agents.tools", [])
    for entry in candidates:
        provider = entry.load()
        if callable(provider):
            provider = provider()
        if not hasattr(provider, "list_tools") or not hasattr(provider, "get_tool_rules"):
            raise ValueError("[kantan-agents][E7] Tool provider must implement list_tools and get_tool_rules")
        provider_tools = provider.list_tools()
        if provider_tools:
            tools.extend(list(provider_tools))
        provider_rules = provider.get_tool_rules()
        if provider_rules is not None:
            rules = merge_tool_rules(rules, provider_rules)
    return tools, rules
