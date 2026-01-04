from types import SimpleNamespace

import pytest

from kantan_agents.agent import Agent


def test_prepare_context_adds_history_list_when_enabled():
    agent = Agent(name="agent", instructions="hello", history=2)
    context = agent._prepare_context({})
    assert context["history"] == []


def test_prepare_context_defaults_when_none():
    agent = Agent(name="agent", instructions="hello", history=1)
    context = agent._prepare_context(None)
    assert context["result"] is None
    assert "tool_rules" in context
    assert context["history"] == []


def test_append_history_respects_limit():
    agent = Agent(name="agent", instructions="hello", history=2)
    context = {"history": []}
    agent._append_history(context, "q1", SimpleNamespace(final_output="a1"))
    agent._append_history(context, "q2", SimpleNamespace(final_output="a2"))
    agent._append_history(context, "q3", SimpleNamespace(final_output="a3"))

    assert len(context["history"]) == 2
    assert context["history"][0]["text"] == "q3"
    assert context["history"][1]["text"] == "a3"


def test_append_history_skips_when_disabled():
    agent = Agent(name="agent", instructions="hello", history=0)
    context = {"history": []}
    agent._append_history(context, "q1", SimpleNamespace(final_output="a1"))
    assert context["history"] == []


def test_prepare_context_rejects_invalid_history():
    agent = Agent(name="agent", instructions="hello", history=1)
    with pytest.raises(ValueError):
        agent._prepare_context({"history": "bad"})
