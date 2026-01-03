from types import SimpleNamespace

import pytest

from kantan_agents.agent import Agent


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

    def get_policy(self):
        return {"allow": ["dummy.tool"], "deny": [], "params": {}}


class InvalidProvider:
    pass


def test_collects_tools_and_policy_from_entry_points(monkeypatch):
    entry_points = DummyEntryPoints([DummyEntryPoint(DummyProvider)])
    monkeypatch.setattr("importlib.metadata.entry_points", lambda: entry_points)

    agent = Agent(name="provider-agent", instructions="Hello")
    assert agent._provider_policy["allow"] == ["dummy.tool"]
    assert any(getattr(tool, "name", None) == "dummy.tool" for tool in agent._tools)


def test_invalid_provider_raises(monkeypatch):
    entry_points = DummyEntryPoints([DummyEntryPoint(InvalidProvider)])
    monkeypatch.setattr("importlib.metadata.entry_points", lambda: entry_points)

    with pytest.raises(ValueError):
        Agent(name="provider-agent", instructions="Hello")
