import os

import pytest
from openai import BadRequestError
from pydantic import BaseModel

from kantan_agents import Agent, set_trace_processors
from kantan_llm.tracing import SQLiteTracer, SpanQuery


class Rubric(BaseModel):
    score: float
    comments: list[str]


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY is required")
def test_trace_records_tool_calls_and_rubric(tmp_path):
    os.environ["OPENAI_DEFAULT_MODEL"] = "gpt-5-mini"

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
        output_type=Rubric,
    )

    try:
        context = agent.run("Assess: Trace quality is important.")
    except BadRequestError as exc:
        if "model_not_found" in str(exc) or "does not exist" in str(exc):
            pytest.skip("gpt-5-mini is not available for this API key")
        raise

    assert context["result"].final_output is not None
    assert isinstance(context["result"].final_output, Rubric)
    assert 0.0 <= context["result"].final_output.score <= 1.0

    spans = tracer.search_spans(query=SpanQuery(limit=50))
    assert spans

    assert any(span.span_type == "function" for span in spans)
    assert any(span.rubric is not None for span in spans)
