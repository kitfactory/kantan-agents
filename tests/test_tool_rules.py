import pytest

from kantan_agents.agent import Agent, _validate_tool_input
from kantan_agents.tool_rules import (
    ToolRulesMode,
    get_context_with_tool_rules,
    is_tool_allowed,
    merge_tool_rules,
    normalize_tool_rules,
    validate_tool_params,
)


def test_get_context_with_tool_rules_mode():
    allow_context = get_context_with_tool_rules(ToolRulesMode.ALLOW_ALL)
    assert allow_context["tool_rules"]["allow"] == "*"
    assert allow_context["tool_rules"]["deny"] == []

    deny_context = get_context_with_tool_rules(ToolRulesMode.DENY_ALL)
    assert deny_context["tool_rules"]["allow"] == []
    assert deny_context["tool_rules"]["deny"] == "*"

    recommended_context = get_context_with_tool_rules(ToolRulesMode.RECOMMENDED)
    assert recommended_context["tool_rules"]["allow"] is None
    assert recommended_context["tool_rules"]["deny"] is None


def test_get_context_with_tool_rules_rejects_invalid_type():
    with pytest.raises(ValueError) as excinfo:
        get_context_with_tool_rules("bad")
    assert str(excinfo.value) == "[kantan-agents][E18] Tool rules must be a dict"


def test_prepare_context_rejects_invalid_tool_rules():
    agent = Agent(name="agent", instructions="hello")
    with pytest.raises(ValueError) as excinfo:
        agent._prepare_context({"tool_rules": "bad"})
    assert str(excinfo.value) == "[kantan-agents][E18] Tool rules must be a dict"


def test_merge_tool_rules_unions_allow_and_deny():
    base = {"allow": ["a"], "deny": ["x"], "params": {"t": {"q": {"type": "string"}}}}
    incoming = {"allow": ["b"], "deny": ["y"], "params": {"t": {"q": {"maxLength": 10}}}}
    merged = merge_tool_rules(base, incoming)

    assert sorted(merged["allow"]) == ["a", "b"]
    assert sorted(merged["deny"]) == ["x", "y"]
    assert merged["params"]["t"]["q"]["type"] == "string"
    assert merged["params"]["t"]["q"]["maxLength"] == 10


def test_is_tool_allowed_denies_on_conflict():
    tool_rules = {"allow": ["tool_a"], "deny": ["tool_a"], "params": {}}
    assert is_tool_allowed(tool_rules, "tool_a") is False


def test_is_tool_allowed_allows_star_except_denied():
    tool_rules = {"allow": "*", "deny": ["blocked"], "params": {}}
    assert is_tool_allowed(tool_rules, "blocked") is False
    assert is_tool_allowed(tool_rules, "ok") is True


def test_normalize_tool_rules_params_non_mapping():
    normalized = normalize_tool_rules({"allow": [], "deny": [], "params": "bad"})
    assert normalized["params"] == {}


def test_normalize_tool_rules_rejects_invalid_type():
    with pytest.raises(ValueError) as excinfo:
        normalize_tool_rules("bad")
    assert str(excinfo.value) == "[kantan-agents][E18] Tool rules must be a dict"


def test_validate_tool_params_checks_rules():
    tool_rules = {
        "allow": ["tool_a"],
        "deny": [],
        "params": {
            "tool_a": {
                "text": {"type": "string", "minLength": 2, "maxLength": 4, "pattern": "^a"},
                "count": {"type": "integer", "minimum": 1, "maximum": 3},
            }
        },
    }
    validate_tool_params(tool_rules, "tool_a", {"text": "ab", "count": 2})
    with pytest.raises(ValueError):
        validate_tool_params(tool_rules, "tool_a", {"text": "b", "count": 2})
    with pytest.raises(ValueError):
        validate_tool_params(tool_rules, "tool_a", {"text": "ab", "count": 0})


def test_validate_tool_input_rejects_invalid_json():
    tool_rules = {"allow": ["tool_a"], "deny": [], "params": {}}
    with pytest.raises(ValueError) as excinfo:
        _validate_tool_input(tool_rules, "tool_a", "{bad")
    assert str(excinfo.value) == "[kantan-agents][E10] Tool input must be a JSON object"
