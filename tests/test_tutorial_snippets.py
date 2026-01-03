import os

import pytest
from openai import BadRequestError
from pydantic import BaseModel

from kantan_agents import Agent, Prompt, RUBRIC, set_trace_processors
from kantan_llm.tracing import SQLiteTracer


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY is required")
def test_tutorial_snippets_smoke(tmp_path):
    os.environ["OPENAI_DEFAULT_MODEL"] = "gpt-5-mini"

    try:
        agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
        context = agent.run("Hello")
        assert context["result"].final_output is not None

        tracer = SQLiteTracer(str(tmp_path / "traces.sqlite3"))
        set_trace_processors([tracer])
        agent = Agent(name="trace-agent", instructions="Answer briefly.")
        context = agent.run("Explain trace metadata in one sentence.")
        assert context["result"].final_output is not None

        prompt = Prompt(
            name="qa",
            version="v1",
            text="Answer the user briefly.",
            meta={"variant": "A"},
        )
        agent = Agent(name="prompted-agent", instructions=prompt)
        context = agent.run("Explain tracing in one sentence.")
        assert context["result"].final_output is not None

        class Summary(BaseModel):
            title: str
            bullets: list[str]

        agent = Agent(
            name="structured-agent",
            instructions="Summarize the input.",
            output_type=Summary,
        )
        context = agent.run("Summarize the release notes.")
        assert isinstance(context["result"].final_output, Summary)

        booking_agent = Agent(name="booking", instructions="Handle booking tasks.")
        refund_agent = Agent(name="refund", instructions="Handle refund tasks.")
        manager = Agent(
            name="manager",
            instructions="Route tasks to specialists.",
            handoffs=[booking_agent, refund_agent],
        )
        context = manager.run("I need a refund for last week's order.")
        assert context["result"].final_output is not None

        def word_count(text: str) -> int:
            return len(text.split())

        agent = Agent(
            name="evaluator",
            instructions="Use word_count and then output a rubric with score and comments.",
            tools=[word_count],
            output_type=RUBRIC,
        )
        context = agent.run("Assess this sentence: 'Tracing enables analysis.'")
        assert isinstance(context["result"].final_output, RUBRIC)
    except BadRequestError as exc:
        if "model_not_found" in str(exc) or "does not exist" in str(exc):
            pytest.skip("gpt-5-mini is not available for this API key")
        raise
