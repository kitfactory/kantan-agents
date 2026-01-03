import agents

from kantan_agents.agent import Agent


def test_handoffs_accept_agent_instances():
    specialist = Agent(name="specialist", instructions="Handle tasks.")
    manager = Agent(name="manager", instructions="Route.", handoffs=[specialist])
    sdk_agent = manager._build_sdk_agent()

    assert isinstance(sdk_agent, agents.Agent)
    assert len(sdk_agent.handoffs) == 1
    assert isinstance(sdk_agent.handoffs[0], agents.Agent)


def test_handoff_instructions_use_context():
    class DummyCtx:
        def __init__(self, context):
            self.context = context

    specialist = Agent(name="specialist", instructions="Handle {{ $ctx.topic }}.")
    manager = Agent(name="manager", instructions="Route.", handoffs=[specialist])
    sdk_agent = manager._build_sdk_agent()
    handoff_agent = sdk_agent.handoffs[0]
    rendered = handoff_agent.instructions(DummyCtx({"topic": "refunds"}), handoff_agent)

    assert rendered == "Handle refunds."
