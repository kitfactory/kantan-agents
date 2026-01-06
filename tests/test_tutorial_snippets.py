import os

import pytest
from openai import BadRequestError
from pydantic import BaseModel

from kantan_agents import Agent, Prompt, RUBRIC, set_trace_processors
from kantan_llm.tracing import SQLiteTracer


def _agent_kwargs(model_env):
    return {
        "model": model_env.model,
        "model_provider_factory": model_env.model_provider_factory,
    }


@pytest.mark.integration
def test_tutorial_snippets_smoke(tmp_path, model_env):
    try:
        agent = Agent(name="basic-agent", instructions="You are a helpful assistant.", **_agent_kwargs(model_env))
        context = agent.run("Hello", {})
        assert context["result"].final_output is not None

        if model_env.name == "lmstudio" and os.getenv("LMSTUDIO_FULL_TUTORIAL") != "1":
            return

        tracer = SQLiteTracer(str(tmp_path / "traces.sqlite3"))
        set_trace_processors([tracer])
        agent = Agent(name="trace-agent", instructions="Answer briefly.", **_agent_kwargs(model_env))
        context = agent.run("Explain trace metadata in one sentence.", {})
        assert context["result"].final_output is not None

        prompt = Prompt(
            name="qa",
            version="v1",
            text="Answer the user briefly.",
            meta={"variant": "A"},
        )
        agent = Agent(name="prompted-agent", instructions=prompt, **_agent_kwargs(model_env))
        context = agent.run("Explain tracing in one sentence.", {})
        assert context["result"].final_output is not None

        class Summary(BaseModel):
            title: str
            bullets: list[str]

        agent = Agent(
            name="structured-agent",
            instructions="Summarize the input.",
            **_agent_kwargs(model_env),
            output_type=Summary,
        )
        context = agent.run("Summarize the release notes.", {})
        assert isinstance(context["result"].final_output, Summary)

        booking_agent = Agent(name="booking", instructions="Handle booking tasks.", **_agent_kwargs(model_env))
        refund_agent = Agent(name="refund", instructions="Handle refund tasks.", **_agent_kwargs(model_env))
        manager = Agent(
            name="manager",
            instructions="Route tasks to specialists.",
            handoffs=[booking_agent, refund_agent],
            **_agent_kwargs(model_env),
        )
        context = manager.run("I need a refund for last week's order.", {})
        assert context["result"].final_output is not None

        def word_count(text: str) -> int:
            return len(text.split())

        agent = Agent(
            name="evaluator",
            instructions="Use word_count and then output a rubric with score and comments.",
            tools=[word_count],
            **_agent_kwargs(model_env),
            output_type=RUBRIC,
        )
        context = agent.run("Assess this sentence: 'Tracing enables analysis.'", {})
        assert isinstance(context["result"].final_output, RUBRIC)
    except BadRequestError as exc:
        if "model_not_found" in str(exc) or "does not exist" in str(exc):
            pytest.skip(f"{model_env.model} is not available for this endpoint")
        raise
