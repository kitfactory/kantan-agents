import asyncio
from types import SimpleNamespace

from kantan_agents.agent import Agent


async def _fake_run(**kwargs):
    return SimpleNamespace(final_output="ok")


def test_run_async_uses_runner(monkeypatch):
    monkeypatch.setattr("agents.Runner.run", _fake_run)
    agent = Agent(name="agent", instructions="hello")
    context = asyncio.run(agent.run_async("Hello"))
    assert context["result"].final_output == "ok"


def test_run_in_running_loop_uses_thread(monkeypatch):
    monkeypatch.setattr("agents.Runner.run", _fake_run)
    agent = Agent(name="agent", instructions="hello")

    async def _runner():
        return agent.run("Hello")

    context = asyncio.run(_runner())
    assert context["result"].final_output == "ok"
