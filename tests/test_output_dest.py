from types import SimpleNamespace

from kantan_agents.agent import Agent


def test_output_dest_stores_structured_output():
    agent = Agent(name="agent", instructions="hello", output_dest="summary")
    context = {}
    agent._store_output_dest(context, SimpleNamespace(final_output={"title": "A"}))
    assert context["summary"] == {"title": "A"}


def test_output_dest_skips_non_structured_output():
    agent = Agent(name="agent", instructions="hello", output_dest="summary")
    context = {}
    agent._store_output_dest(context, SimpleNamespace(final_output="text"))
    assert "summary" not in context


def test_output_dest_overwrites_existing():
    agent = Agent(name="agent", instructions="hello", output_dest="summary")
    context = {"summary": {"title": "old"}}
    agent._store_output_dest(context, SimpleNamespace(final_output={"title": "new"}))
    assert context["summary"] == {"title": "new"}
