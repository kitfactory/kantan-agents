from types import SimpleNamespace

import pytest

from kantan_agents.agent import Agent
from kantan_llm import AsyncClientBundle, KantanAsyncLLM


def test_agent_resolves_model_name(monkeypatch):
    called = {}

    def fake_get_llm(name):
        called["name"] = name
        return object()

    created = {}

    def fake_agent(**kwargs):
        created.update(kwargs)
        return SimpleNamespace(**kwargs)

    monkeypatch.setattr("kantan_agents.agent.get_llm", fake_get_llm)
    monkeypatch.setattr("agents.Agent", fake_agent)

    agent = Agent(name="agent", instructions="hello", model="gpt-test")
    sdk_agent = agent._build_sdk_agent()

    assert called["name"] == "gpt-test"
    assert created["model"] == "gpt-test"
    assert sdk_agent.model == "gpt-test"


def test_agent_rejects_unknown_model(monkeypatch):
    def fake_get_llm(_):
        raise RuntimeError("missing")

    monkeypatch.setattr("kantan_agents.agent.get_llm", fake_get_llm)

    with pytest.raises(ValueError) as excinfo:
        Agent(name="agent", instructions="hello", model="bad-model")

    assert str(excinfo.value) == "[kantan-agents][E19] Model not found: bad-model"


def test_agent_accepts_async_client_bundle(monkeypatch):
    client = object()
    bundle = AsyncClientBundle(client=client, model="gpt-test", provider="openai", base_url=None)
    captured = {}

    class FakeProvider:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr("kantan_agents.agent.OpenAIProvider", FakeProvider)

    agent = Agent(name="agent", instructions="hello", model=bundle)
    agent._model_provider_factory()

    assert agent._model == "gpt-test"
    assert captured["openai_client"] is client
    assert captured["use_responses"] is True


def test_agent_accepts_kantan_async_llm(monkeypatch):
    client = object()
    llm = KantanAsyncLLM(provider="lmstudio", model="openai/gpt-oss-20b", client=client)
    captured = {}

    class FakeProvider:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr("kantan_agents.agent.OpenAIProvider", FakeProvider)

    agent = Agent(name="agent", instructions="hello", model=llm)
    agent._model_provider_factory()

    assert agent._model == "openai/gpt-oss-20b"
    assert captured["openai_client"] is client
    assert captured["use_responses"] is False
