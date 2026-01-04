from __future__ import annotations

from typing import Any, Mapping

import agents
from agents.tool import FunctionTool

from .tool_rules import ToolRulesMode, merge_tool_rules, normalize_tool_rules
from .tool_registry import collect_tool_providers


def list_provider_tools() -> list[str]:
    tools, _ = collect_tool_providers()
    names: list[str] = []
    for tool in tools:
        name = _tool_name_for_listing(tool)
        if not name:
            raise ValueError("[kantan-agents][E4] Tool must define name")
        if name not in names:
            names.append(name)
    return names


def get_provider_tool_rules() -> dict[str, Any]:
    _, provider_rules = collect_tool_providers()
    return normalize_tool_rules(provider_rules)


def get_effective_tool_rules(
    *,
    context: dict | None = None,
    tool_rules: Mapping[str, Any] | ToolRulesMode | None = None,
) -> dict[str, Any]:
    if context is not None and not isinstance(context, dict):
        raise ValueError("[kantan-agents][E5] Context must be a dict")
    explicit = tool_rules
    if explicit is None and context is not None:
        explicit = context.get("tool_rules")
    _, provider_rules = collect_tool_providers()
    merged = merge_tool_rules(None, provider_rules)
    return merge_tool_rules(merged, explicit)


def _tool_name_for_listing(tool: Any) -> str | None:
    if isinstance(tool, FunctionTool):
        return tool.name
    if callable(tool):
        return agents.function_tool(tool).name
    return getattr(tool, "name", None)
