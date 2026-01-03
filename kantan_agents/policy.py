from __future__ import annotations

import re
from enum import Enum
from typing import Any, Mapping


class PolicyMode(Enum):
    ALLOW_ALL = "allow_all"
    DENY_ALL = "deny_all"
    RECOMMENDED = "recommended"


def get_context_with_policy(mode_or_policy: PolicyMode | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(mode_or_policy, PolicyMode):
        policy = policy_from_mode(mode_or_policy)
    else:
        policy = dict(mode_or_policy)
    return {"policy": policy, "result": None}


def policy_from_mode(mode: PolicyMode) -> dict[str, Any]:
    if mode is PolicyMode.ALLOW_ALL:
        return {"allow": "*", "deny": [], "params": {}}
    if mode is PolicyMode.DENY_ALL:
        return {"allow": [], "deny": "*", "params": {}}
    if mode is PolicyMode.RECOMMENDED:
        return {"allow": None, "deny": None, "params": {}}
    raise ValueError(f"[kantan-agents][E9] Unknown PolicyMode: {mode}")


def normalize_policy(policy: Mapping[str, Any] | PolicyMode | None) -> dict[str, Any]:
    if policy is None:
        return {"allow": None, "deny": None, "params": {}}
    if isinstance(policy, PolicyMode):
        policy = policy_from_mode(policy)
    allow = policy.get("allow")
    deny = policy.get("deny")
    params = policy.get("params") or {}
    if not isinstance(params, Mapping):
        params = {}
    return {"allow": allow, "deny": deny, "params": dict(params)}


def merge_policies(base: Mapping[str, Any] | PolicyMode | None, incoming: Mapping[str, Any] | PolicyMode | None) -> dict[str, Any]:
    base_norm = normalize_policy(base)
    incoming_norm = normalize_policy(incoming)
    merged_allow = _merge_allow_deny(base_norm["allow"], incoming_norm["allow"])
    merged_deny = _merge_allow_deny(base_norm["deny"], incoming_norm["deny"])
    merged_params = _merge_params(base_norm["params"], incoming_norm["params"])
    return {"allow": merged_allow, "deny": merged_deny, "params": merged_params}


def is_tool_allowed(policy: Mapping[str, Any] | None, tool_name: str) -> bool:
    if not policy:
        return True
    deny = policy.get("deny")
    if deny == "*" or (isinstance(deny, list) and tool_name in deny):
        return False
    allow = policy.get("allow")
    if allow is None:
        return True
    if allow == "*":
        return True
    if isinstance(allow, list):
        return tool_name in allow
    return True


def validate_tool_params(policy: Mapping[str, Any] | None, tool_name: str, arguments: Mapping[str, Any]) -> None:
    if not policy:
        return
    params = policy.get("params") or {}
    rules = params.get(tool_name)
    if not isinstance(rules, Mapping):
        return
    for param_name, rule in rules.items():
        if param_name not in arguments:
            continue
        _validate_param_rule(tool_name, param_name, arguments[param_name], rule)


def _validate_param_rule(tool_name: str, param_name: str, value: Any, rule: Any) -> None:
    if not isinstance(rule, Mapping):
        return
    if "type" in rule:
        if not _check_type(value, rule["type"]):
            raise ValueError(f"[kantan-agents][E11] Tool parameter type mismatch: {tool_name}.{param_name}")
    if "enum" in rule:
        allowed = rule["enum"]
        if isinstance(allowed, list) and value not in allowed:
            raise ValueError(f"[kantan-agents][E12] Tool parameter enum mismatch: {tool_name}.{param_name}")
    if isinstance(value, str):
        if "minLength" in rule and len(value) < int(rule["minLength"]):
            raise ValueError(f"[kantan-agents][E13] Tool parameter minLength mismatch: {tool_name}.{param_name}")
        if "maxLength" in rule and len(value) > int(rule["maxLength"]):
            raise ValueError(f"[kantan-agents][E14] Tool parameter maxLength mismatch: {tool_name}.{param_name}")
        if "pattern" in rule:
            pattern = rule["pattern"]
            if not isinstance(pattern, str) or re.search(pattern, value) is None:
                raise ValueError(f"[kantan-agents][E15] Tool parameter pattern mismatch: {tool_name}.{param_name}")
    if isinstance(value, (int, float)):
        if "minimum" in rule and value < float(rule["minimum"]):
            raise ValueError(f"[kantan-agents][E16] Tool parameter minimum mismatch: {tool_name}.{param_name}")
        if "maximum" in rule and value > float(rule["maximum"]):
            raise ValueError(f"[kantan-agents][E17] Tool parameter maximum mismatch: {tool_name}.{param_name}")


def _check_type(value: Any, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return True


def _merge_allow_deny(base: Any, incoming: Any) -> Any:
    if base is None:
        return incoming
    if incoming is None:
        return base
    if base == "*" or incoming == "*":
        return "*"
    if not isinstance(base, list):
        base_list = [base]
    else:
        base_list = base
    if not isinstance(incoming, list):
        incoming_list = [incoming]
    else:
        incoming_list = incoming
    merged = []
    for name in base_list + incoming_list:
        if name not in merged:
            merged.append(name)
    return merged


def _merge_params(base: Mapping[str, Any], incoming: Mapping[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {**base}
    for tool_name, rules in incoming.items():
        if not isinstance(rules, Mapping):
            merged[tool_name] = rules
            continue
        current = merged.get(tool_name, {})
        if not isinstance(current, Mapping):
            merged[tool_name] = dict(rules)
            continue
        updated: dict[str, Any] = dict(current)
        for param_name, rule in rules.items():
            current_rule = updated.get(param_name)
            if isinstance(current_rule, Mapping) and isinstance(rule, Mapping):
                merged_rule = dict(current_rule)
                merged_rule.update(rule)
                updated[param_name] = merged_rule
            else:
                updated[param_name] = rule
        merged[tool_name] = updated
    return merged
