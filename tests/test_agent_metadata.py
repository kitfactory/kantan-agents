from kantan_agents.agent import Agent
from kantan_agents.prompt import Prompt
from kantan_agents.utils import hash_text


def test_trace_metadata_with_prompt_instructions():
    prompt = Prompt(name="p", version="v1", text="hello", meta={"variant": "A"})
    agent = Agent(name="agent", instructions=prompt)
    metadata = agent._build_trace_metadata({"existing": "x", "prompt_name": "override"})

    assert metadata["agent_name"] == "agent"
    assert metadata["prompt_name"] == "p"
    assert metadata["prompt_version"] == "v1"
    assert metadata["prompt_id"] == hash_text("hello")
    assert metadata["prompt_meta_variant"] == "A"
    assert metadata["existing"] == "x"


def test_trace_metadata_with_string_instructions():
    agent = Agent(name="agent", instructions="hello")
    metadata = agent._build_trace_metadata({})

    assert metadata["agent_name"] == "agent"
    assert metadata["prompt_name"] == "agent"
    assert metadata["prompt_id"] == hash_text("hello")
