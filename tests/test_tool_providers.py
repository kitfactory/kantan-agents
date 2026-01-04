from types import SimpleNamespace

import pytest

from kantan_agents.agent import Agent
from kantan_agents.tools_info import (
    get_effective_tool_rules,
    get_provider_tool_rules,
    list_provider_tools,
)


class DummyEntryPoint:
    def __init__(self, provider):
        self._provider = provider

    def load(self):
        return self._provider


class DummyEntryPoints:
    def __init__(self, entries):
        self._entries = entries

    def select(self, *, group: str):
        if group == "kantan_agents.tools":
            return list(self._entries)
        return []


class DummyTool:
    name = "dummy.tool"


class DummyProvider:
    def list_tools(self):
        return [DummyTool()]

    def get_tool_rules(self):
        return {"allow": ["dummy.tool"], "deny": [], "params": {}}


class InvalidProvider:
    pass


def test_collects_tools_and_rules_from_entry_points(monkeypatch):
    entry_points = DummyEntryPoints([DummyEntryPoint(DummyProvider)])
    monkeypatch.setattr("importlib.metadata.entry_points", lambda: entry_points)

    agent = Agent(name="provider-agent", instructions="Hello")
    assert agent._provider_tool_rules["allow"] == ["dummy.tool"]
    assert any(getattr(tool, "name", None) == "dummy.tool" for tool in agent._tools)


def test_invalid_provider_raises(monkeypatch):
    entry_points = DummyEntryPoints([DummyEntryPoint(InvalidProvider)])
    monkeypatch.setattr("importlib.metadata.entry_points", lambda: entry_points)

    with pytest.raises(ValueError):
        Agent(name="provider-agent", instructions="Hello")


def test_list_provider_tools(monkeypatch):
    entry_points = DummyEntryPoints([DummyEntryPoint(DummyProvider)])
    monkeypatch.setattr("importlib.metadata.entry_points", lambda: entry_points)

    assert list_provider_tools() == ["dummy.tool"]


def test_get_provider_tool_rules(monkeypatch):
    entry_points = DummyEntryPoints([DummyEntryPoint(DummyProvider)])
    monkeypatch.setattr("importlib.metadata.entry_points", lambda: entry_points)

    settings = get_provider_tool_rules()
    assert settings["allow"] == ["dummy.tool"]


def test_get_effective_tool_rules_merges(monkeypatch):
    entry_points = DummyEntryPoints([DummyEntryPoint(DummyProvider)])
    monkeypatch.setattr("importlib.metadata.entry_points", lambda: entry_points)

    context = {
        "tool_rules": {
            "allow": ["extra.tool"],
            "deny": [],
            "params": {"extra.tool": {"text": {"type": "string"}}},
        }
    }
    settings = get_effective_tool_rules(context=context)
    assert sorted(settings["allow"]) == ["dummy.tool", "extra.tool"]
    assert settings["params"]["extra.tool"]["text"]["type"] == "string"
