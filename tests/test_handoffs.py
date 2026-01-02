import agents

from kantan_agents.agent import Agent


def test_handoffs_accept_agent_instances():
    specialist = Agent(name="specialist", instructions="Handle tasks.")
    manager = Agent(name="manager", instructions="Route.", handoffs=[specialist])
    sdk_agent = manager._build_sdk_agent("Route.")

    assert isinstance(sdk_agent, agents.Agent)
    assert len(sdk_agent.handoffs) == 1
    assert isinstance(sdk_agent.handoffs[0], agents.Agent)
