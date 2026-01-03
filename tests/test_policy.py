import pytest

from kantan_agents.policy import (
    PolicyMode,
    get_context_with_policy,
    is_tool_allowed,
    merge_policies,
    normalize_policy,
    validate_tool_params,
)


def test_get_context_with_policy_mode():
    allow_context = get_context_with_policy(PolicyMode.ALLOW_ALL)
    assert allow_context["policy"]["allow"] == "*"
    assert allow_context["policy"]["deny"] == []

    deny_context = get_context_with_policy(PolicyMode.DENY_ALL)
    assert deny_context["policy"]["allow"] == []
    assert deny_context["policy"]["deny"] == "*"


def test_merge_policies_unions_allow_and_deny():
    base = {"allow": ["a"], "deny": ["x"], "params": {"t": {"q": {"type": "string"}}}}
    incoming = {"allow": ["b"], "deny": ["y"], "params": {"t": {"q": {"maxLength": 10}}}}
    merged = merge_policies(base, incoming)

    assert sorted(merged["allow"]) == ["a", "b"]
    assert sorted(merged["deny"]) == ["x", "y"]
    assert merged["params"]["t"]["q"]["type"] == "string"
    assert merged["params"]["t"]["q"]["maxLength"] == 10


def test_is_tool_allowed_denies_on_conflict():
    policy = {"allow": ["tool_a"], "deny": ["tool_a"], "params": {}}
    assert is_tool_allowed(policy, "tool_a") is False


def test_is_tool_allowed_allows_star_except_denied():
    policy = {"allow": "*", "deny": ["blocked"], "params": {}}
    assert is_tool_allowed(policy, "blocked") is False
    assert is_tool_allowed(policy, "ok") is True


def test_normalize_policy_params_non_mapping():
    normalized = normalize_policy({"allow": [], "deny": [], "params": "bad"})
    assert normalized["params"] == {}


def test_validate_tool_params_checks_rules():
    policy = {
        "allow": ["tool_a"],
        "deny": [],
        "params": {
            "tool_a": {
                "text": {"type": "string", "minLength": 2, "maxLength": 4, "pattern": "^a"},
                "count": {"type": "integer", "minimum": 1, "maximum": 3},
            }
        },
    }
    validate_tool_params(policy, "tool_a", {"text": "ab", "count": 2})
    with pytest.raises(ValueError):
        validate_tool_params(policy, "tool_a", {"text": "b", "count": 2})
    with pytest.raises(ValueError):
        validate_tool_params(policy, "tool_a", {"text": "ab", "count": 0})
