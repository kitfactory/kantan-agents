import os

import pytest
from openai import BadRequestError
from pydantic import BaseModel

from kantan_agents import Agent, set_trace_processors


class CaptureProcessor:
    def __init__(self) -> None:
        self.spans = []
        self.trace = None

    def on_trace_start(self, trace):
        self.trace = trace

    def on_trace_end(self, trace):
        self.trace = trace

    def on_span_start(self, span):
        return None

    def on_span_end(self, span):
        exported = span.export()
        if exported is not None:
            self.spans.append(exported)

    def shutdown(self) -> None:
        return None

    def force_flush(self) -> None:
        return None


class Rubric(BaseModel):
    score: float
    comments: list[str]


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY is required")
def test_trace_records_tool_calls_and_rubric():
    os.environ["OPENAI_DEFAULT_MODEL"] = "gpt-5.1-mini"

    def word_count(text: str) -> int:
        return len(text.split())

    processor = CaptureProcessor()
    set_trace_processors([processor])

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
        result = agent.run("Assess: Trace quality is important.")
    except BadRequestError as exc:
        if "model_not_found" in str(exc) or "does not exist" in str(exc):
            pytest.skip("gpt-5.1-mini is not available for this API key")
        raise

    assert result.final_output is not None
    assert isinstance(result.final_output, Rubric)
    assert 0.0 <= result.final_output.score <= 1.0

    assert processor.trace is not None
    span_types = [span.get("span_data", {}).get("type") for span in processor.spans]
    assert "function" in span_types
    assert "generation" in span_types

    output_blobs = [span.get("span_data", {}).get("output") for span in processor.spans]
    assert any("rubric" in str(blob) for blob in output_blobs)
