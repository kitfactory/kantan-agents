import os

import pytest
from openai import BadRequestError
from pydantic import BaseModel

from kantan_agents import Agent, Prompt, set_trace_processors
from kantan_llm.tracing import SQLiteTracer, SpanQuery
from kantan_llm.tracing import TraceQuery

from kantan_agents.utils import hash_text

class Rubric(BaseModel):
    score: float
    comments: list[str]

def _agent_kwargs(model_env):
    return {
        "model": model_env.model,
        "model_provider_factory": model_env.model_provider_factory,
    }


@pytest.mark.integration
def test_trace_records_tool_calls_and_rubric(tmp_path, model_env):
    def word_count(text: str) -> int:
        return len(text.split())

    tracer = SQLiteTracer(str(tmp_path / "traces.sqlite3"))
    set_trace_processors([tracer])

    agent = Agent(
        name="trace-evaluator",
        instructions=(
            "You must call the word_count tool with the full user input. "
            "Then output a rubric with score (0-1) and comments."
        ),
        tools=[word_count],
        **_agent_kwargs(model_env),
        output_type=Rubric,
    )

    try:
        context = agent.run("Assess: Trace quality is important.", {})
    except BadRequestError as exc:
        if "model_not_found" in str(exc) or "does not exist" in str(exc):
            pytest.skip(f"{model_env.model} is not available for this endpoint")
        raise

    assert context["result"].final_output is not None
    assert isinstance(context["result"].final_output, Rubric)
    strict_rubric = model_env.name != "lmstudio" or os.getenv("LMSTUDIO_STRICT_RUBRIC") == "1"
    if strict_rubric:
        assert 0.0 <= context["result"].final_output.score <= 1.0

    spans = tracer.search_spans(query=SpanQuery(limit=50))
    assert spans

    supports_tools = model_env.name != "lmstudio" or os.getenv("LMSTUDIO_SUPPORTS_TOOLS") == "1"
    if supports_tools:
        assert any(span.span_type == "function" for span in spans)
    assert any(span.rubric is not None for span in spans)


@pytest.mark.integration
def test_trace_records_prompt_metadata(tmp_path, model_env):
    tracer = SQLiteTracer(str(tmp_path / "traces.sqlite3"))
    set_trace_processors([tracer])

    prompt = Prompt(
        name="qa",
        version="v1",
        text="Answer the user briefly.",
        meta={"variant": "A"},
    )
    agent = Agent(name="prompted-agent", instructions=prompt, **_agent_kwargs(model_env))

    try:
        context = agent.run("Explain tracing in one sentence.", {})
    except BadRequestError as exc:
        if "model_not_found" in str(exc) or "does not exist" in str(exc):
            pytest.skip(f"{model_env.model} is not available for this endpoint")
        raise

    assert context["result"].final_output is not None

    traces = tracer.search_traces(query=TraceQuery(limit=1))
    assert traces
    metadata = traces[0].metadata or {}

    assert metadata["agent_name"] == "prompted-agent"
    assert metadata["prompt_name"] == "qa"
    assert metadata["prompt_version"] == "v1"
    assert metadata["prompt_id"] == hash_text("Answer the user briefly.")
    assert metadata["prompt_meta_variant"] == "A"


@pytest.mark.integration
def test_rubric_judges_generated_output(tmp_path, model_env):
    tracer = SQLiteTracer(str(tmp_path / "traces.sqlite3"))
    set_trace_processors([tracer])

    prompt_a = Prompt(
        name="A",
        version="v1",
        text="Write a short, clear explanation of trace metadata in one sentence.",
        meta={"role": "generator"},
    )
    generator = Agent(name="generator", instructions=prompt_a, **_agent_kwargs(model_env))

    try:
        context = generator.run("Explain trace metadata.", {})
    except BadRequestError as exc:
        if "model_not_found" in str(exc) or "does not exist" in str(exc):
            pytest.skip(f"{model_env.model} is not available for this endpoint")
        raise

    generated = context["result"].final_output
    assert generated is not None

    prompt_judge = Prompt(
        name="A-judge",
        version="v1",
        text=(
            "Evaluate the following answer and output a rubric with score (0-1) and comments."
        ),
        meta={"role": "judge"},
    )
    judge_agent = Agent(
        name="judge",
        instructions=prompt_judge,
        **_agent_kwargs(model_env),
        output_type=Rubric,
    )

    try:
        judge_context = judge_agent.run(str(generated), {})
    except BadRequestError as exc:
        if "model_not_found" in str(exc) or "does not exist" in str(exc):
            pytest.skip(f"{model_env.model} is not available for this endpoint")
        raise

    assert isinstance(judge_context["result"].final_output, Rubric)
    strict_rubric = model_env.name != "lmstudio" or os.getenv("LMSTUDIO_STRICT_RUBRIC") == "1"
    if strict_rubric:
        assert 0.0 <= judge_context["result"].final_output.score <= 1.0

    spans = tracer.search_spans(query=SpanQuery(limit=50))
    assert any(span.rubric is not None for span in spans)
