from __future__ import annotations

import asyncio
import uuid
from typing import Any, Callable, Mapping

import agents
from agents.tool import FunctionTool

from .prompt import Prompt
from .utils import flatten_prompt_meta, hash_text, render_template


Renderer = Callable[[str, Mapping[str, Any] | None], str]


def default_renderer(text: str, render_vars: Mapping[str, Any] | None) -> str:
    return render_template(text, render_vars)


class Agent:
    def __init__(
        self,
        name: str,
        instructions: str | Prompt,
        *,
        tools: list | None = None,
        renderer: Renderer | None = None,
        metadata: dict | None = None,
        output_type: type | None = None,
        handoffs: list | None = None,
    ) -> None:
        if instructions is None:
            raise ValueError("[kantan-agents][E1] instructions is required")
        self._name = name
        self._instructions = instructions
        self._tools = self._normalize_tools(tools)
        self._renderer = renderer or default_renderer
        self._metadata = dict(metadata) if metadata is not None else {}
        self._output_type = output_type
        self._handoffs = list(handoffs) if handoffs is not None else []

    @property
    def name(self) -> str:
        return self._name

    def run(
        self,
        input: str,
        *,
        render_vars: dict | None = None,
        trace_metadata: dict | None = None,
    ) -> Any:
        return asyncio.run(self._arun(input, render_vars=render_vars, trace_metadata=trace_metadata))

    async def _arun(
        self,
        input: str,
        *,
        render_vars: dict | None,
        trace_metadata: dict | None,
    ) -> Any:
        rendered_instructions = self._render_instructions(render_vars)
        sdk_agent = self._build_sdk_agent(rendered_instructions)
        merged_metadata = self._build_trace_metadata(trace_metadata)
        run_config = agents.RunConfig(trace_metadata=merged_metadata)
        run_result = await agents.Runner.run(
            starting_agent=sdk_agent,
            input=input,
            run_config=run_config,
        )
        return run_result

    def _render_instructions(self, render_vars: Mapping[str, Any] | None) -> str:
        if isinstance(self._instructions, Prompt):
            text = self._instructions.text
        else:
            text = self._instructions
        return self._renderer(text, render_vars)

    def _build_sdk_agent(self, instructions: str) -> agents.Agent:
        handoffs = [self._resolve_handoff(h) for h in self._handoffs]
        return agents.Agent(
            name=self._name,
            instructions=instructions,
            tools=self._tools,
            handoffs=handoffs,
            output_type=self._output_type,
        )

    def _resolve_handoff(self, handoff: Any) -> Any:
        if isinstance(handoff, Agent):
            rendered = handoff._render_instructions(None)
            return handoff._build_sdk_agent(rendered)
        return handoff

    def _normalize_tools(self, tools: list | None) -> list:
        if tools is None:
            return []
        normalized: list = []
        for tool in tools:
            if isinstance(tool, FunctionTool):
                normalized.append(tool)
            elif callable(tool):
                normalized.append(agents.function_tool(tool))
            else:
                normalized.append(tool)
        return normalized

    def _build_trace_metadata(self, trace_metadata: dict | None) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        merged.update(self._metadata)
        if trace_metadata:
            merged.update(trace_metadata)

        auto = {
            "agent_name": self._name,
            "agent_run_id": uuid.uuid4().hex,
        }

        if isinstance(self._instructions, Prompt):
            prompt = self._instructions
            auto.update(
                {
                    "prompt_name": prompt.name,
                    "prompt_version": prompt.version,
                    "prompt_id": prompt.resolve_id(),
                }
            )
            auto.update(flatten_prompt_meta(prompt.meta))
        else:
            auto.update(
                {
                    "prompt_name": self._name,
                    "prompt_id": hash_text(str(self._instructions)),
                }
            )

        merged.update(auto)
        return merged
