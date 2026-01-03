from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import importlib.metadata
import inspect
import json
import uuid
from typing import Any, Callable, Mapping, Sequence

import agents
from agents.tool import FunctionTool
from agents.tracing import generation_span
from agents.lifecycle import RunHooksBase
try:
    from pydantic import BaseModel
except Exception:  # pragma: no cover - fallback if pydantic is unavailable
    BaseModel = None

from .prompt import Prompt
from .policy import (
    PolicyMode,
    is_tool_allowed,
    merge_policies,
    normalize_policy,
    validate_tool_params,
)
from .utils import flatten_prompt_meta, hash_text, render_template


Renderer = Callable[[str, Mapping[str, Any] | None, bool], str]


def default_renderer(text: str, context: Mapping[str, Any] | None, allow_env: bool) -> str:
    return render_template(text, context, allow_env)


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
        allow_env: bool = False,
        history: int = 50,
        output_dest: str | None = None,
    ) -> None:
        if instructions is None:
            raise ValueError("[kantan-agents][E1] instructions is required")
        self._name = name
        self._instructions = instructions
        provider_tools, provider_policy = _collect_tool_providers()
        self._provider_policy = provider_policy
        self._tools = self._normalize_tools(_merge_tools(provider_tools, tools))
        self._renderer = renderer or default_renderer
        self._metadata = dict(metadata) if metadata is not None else {}
        self._output_type = output_type
        self._handoffs = list(handoffs) if handoffs is not None else []
        self._allow_env = allow_env
        self._history = history
        self._output_dest = output_dest

    @property
    def name(self) -> str:
        return self._name

    def run(
        self,
        input: str,
        context: dict | None = None,
    ) -> dict:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self._arun(input, context=context))
        return _run_in_thread(lambda: self._arun(input, context=context))

    async def run_async(
        self,
        input: str,
        context: dict | None = None,
    ) -> dict:
        return await self._arun(input, context=context)

    async def _arun(
        self,
        input: str,
        context: dict | None,
    ) -> dict:
        context = self._prepare_context(context)
        sdk_agent = self._build_sdk_agent()
        merged_metadata = self._build_trace_metadata()
        run_config = agents.RunConfig(trace_metadata=merged_metadata)
        hooks = _OutputTraceHooks(self._output_type)
        run_result = await agents.Runner.run(
            starting_agent=sdk_agent,
            input=input,
            context=context,
            run_config=run_config,
            hooks=hooks,
        )
        self._store_output_dest(context, run_result)
        self._append_history(context, input, run_result)
        context["result"] = run_result
        return context

    def _render_instructions(self, context: Mapping[str, Any] | None) -> str:
        if isinstance(self._instructions, Prompt):
            text = self._instructions.text
        else:
            text = self._instructions
        return self._call_renderer(text, context)

    def _call_renderer(self, text: str, context: Mapping[str, Any] | None) -> str:
        try:
            params = inspect.signature(self._renderer).parameters
        except (TypeError, ValueError):
            return self._renderer(text, context, self._allow_env)
        if len(params) >= 3:
            return self._renderer(text, context, self._allow_env)
        return self._renderer(text, context)

    def _build_sdk_agent(self) -> agents.Agent:
        handoffs = [self._resolve_handoff(h) for h in self._handoffs]
        return agents.Agent(
            name=self._name,
            instructions=self._instruction_callable,
            tools=self._tools,
            handoffs=handoffs,
            output_type=self._output_type,
        )

    def _instruction_callable(self, ctx, agent) -> str:
        context = getattr(ctx, "context", None)
        if not isinstance(context, Mapping):
            context = None
        return self._render_instructions(context)

    def _resolve_handoff(self, handoff: Any) -> Any:
        if isinstance(handoff, Agent):
            return handoff._build_sdk_agent()
        return handoff

    def _normalize_tools(self, tools: Sequence | None) -> list:
        if not tools:
            return []
        normalized: dict[str, Any] = {}
        for tool in tools:
            normalized_tool = self._coerce_tool(tool)
            tool_name = _tool_name(normalized_tool)
            if not tool_name:
                raise ValueError("[kantan-agents][E4] Tool must define name")
            normalized[tool_name] = normalized_tool
        return [self._wrap_tool_with_policy(tool) for tool in normalized.values()]

    def _coerce_tool(self, tool: Any) -> Any:
        if isinstance(tool, FunctionTool):
            return tool
        if callable(tool):
            return agents.function_tool(tool)
        return tool

    def _wrap_tool_with_policy(self, tool: Any) -> Any:
        if not isinstance(tool, FunctionTool):
            return tool
        tool_name = tool.name
        original_is_enabled = tool.is_enabled

        async def _is_enabled(ctx, agent) -> bool:
            policy = _extract_policy(ctx.context)
            if not is_tool_allowed(policy, tool_name):
                return False
            return await _eval_is_enabled(original_is_enabled, ctx, agent)

        async def _on_invoke_tool(ctx, input_text: str) -> Any:
            policy = _extract_policy(ctx.context)
            if not is_tool_allowed(policy, tool_name):
                raise ValueError(f"[kantan-agents][E8] Tool is not allowed: {tool_name}")
            _validate_tool_input(policy, tool_name, input_text)
            return await tool.on_invoke_tool(ctx, input_text)

        return FunctionTool(
            name=tool.name,
            description=tool.description,
            params_json_schema=tool.params_json_schema,
            on_invoke_tool=_on_invoke_tool,
            strict_json_schema=tool.strict_json_schema,
            is_enabled=_is_enabled,
            tool_input_guardrails=tool.tool_input_guardrails,
            tool_output_guardrails=tool.tool_output_guardrails,
        )

    def _prepare_context(self, context: dict | None) -> dict:
        if context is None:
            context = {}
        if not isinstance(context, dict):
            raise ValueError("[kantan-agents][E5] Context must be a dict")
        resolved_policy = self._resolve_policy(context.get("policy"))
        context["policy"] = resolved_policy
        context.setdefault("result", None)
        if self._history > 0:
            history = context.setdefault("history", [])
            if not isinstance(history, list):
                raise ValueError("[kantan-agents][E6] Context history must be a list")
        return context

    def _append_history(self, context: dict, user_input: str, run_result: Any) -> None:
        if self._history <= 0:
            return
        history = context.setdefault("history", [])
        if not isinstance(history, list):
            raise ValueError("[kantan-agents][E6] Context history must be a list")
        history.append({"role": "user", "text": user_input})
        if run_result is None:
            output_text = ""
        else:
            final_output = getattr(run_result, "final_output", run_result)
            output_text = "" if final_output is None else str(final_output)
        history.append({"role": "assistant", "text": output_text})
        if len(history) > self._history:
            del history[:-self._history]

    def _store_output_dest(self, context: dict, run_result: Any) -> None:
        if not self._output_dest:
            return
        output_value = _structured_output(run_result)
        if output_value is None:
            return
        context[self._output_dest] = output_value

    def _resolve_policy(self, explicit_policy: Mapping[str, Any] | PolicyMode | None) -> dict[str, Any]:
        merged = merge_policies(None, self._provider_policy)
        return merge_policies(merged, explicit_policy)

    def _build_trace_metadata(self) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        merged.update(self._metadata)

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


class _OutputTraceHooks(RunHooksBase[Any, Any]):
    def __init__(self, output_type: type | None) -> None:
        self._output_type = output_type

    async def on_agent_end(self, context, agent, output: Any) -> None:
        payload = _output_payload(output, self._output_type)
        if payload is None:
            return
        with generation_span(output=payload):
            return


def _output_payload(output: Any, output_type: type | None) -> Any | None:
    if output is None:
        return None
    if BaseModel is not None and isinstance(output, BaseModel):
        output_dict = output.model_dump()
    elif hasattr(output, "dict") and callable(getattr(output, "dict")):
        output_dict = output.dict()
    elif isinstance(output, dict):
        output_dict = output
    else:
        return None

    if (
        output_type is not None
        and getattr(output_type, "__name__", None) == "_RubricSchema"
        and isinstance(output_dict, dict)
    ):
        return {"rubric": output_dict}

    if isinstance(output_dict, dict) and {"score", "comments"} <= set(output_dict.keys()):
        return {"rubric": output_dict}

    return output_dict


def _structured_output(run_result: Any) -> dict | None:
    if run_result is None:
        return None
    output = getattr(run_result, "final_output", run_result)
    if output is None:
        return None
    if BaseModel is not None and isinstance(output, BaseModel):
        return output.model_dump()
    if hasattr(output, "dict") and callable(getattr(output, "dict")):
        return output.dict()
    if isinstance(output, dict):
        return output
    return None


def _merge_tools(provider_tools: Sequence | None, tools: Sequence | None) -> list:
    merged: list = []
    if provider_tools:
        merged.extend(list(provider_tools))
    if tools:
        merged.extend(list(tools))
    return merged


def _collect_tool_providers() -> tuple[list, dict | None]:
    tools: list = []
    policy: dict | None = None
    entry_points = importlib.metadata.entry_points()
    if hasattr(entry_points, "select"):
        candidates = entry_points.select(group="kantan_agents.tools")
    else:
        candidates = entry_points.get("kantan_agents.tools", [])
    for entry in candidates:
        provider = entry.load()
        if callable(provider):
            provider = provider()
        if not hasattr(provider, "list_tools") or not hasattr(provider, "get_policy"):
            raise ValueError("[kantan-agents][E7] Tool provider must implement list_tools and get_policy")
        provider_tools = provider.list_tools()
        if provider_tools:
            tools.extend(list(provider_tools))
        provider_policy = provider.get_policy()
        if provider_policy is not None:
            policy = merge_policies(policy, provider_policy)
    return tools, policy


def _tool_name(tool: Any) -> str | None:
    return getattr(tool, "name", None)


async def _eval_is_enabled(value, ctx, agent) -> bool:
    if callable(value):
        result = value(ctx, agent)
        if asyncio.iscoroutine(result):
            return bool(await result)
        return bool(result)
    return bool(value)


def _extract_policy(context: Any) -> dict[str, Any] | None:
    if not isinstance(context, Mapping):
        return None
    policy = context.get("policy")
    return normalize_policy(policy) if policy is not None else None


def _validate_tool_input(policy: Mapping[str, Any] | None, tool_name: str, input_text: str) -> None:
    if not policy:
        return
    if input_text:
        try:
            payload = json.loads(input_text)
        except Exception as exc:
            raise ValueError("[kantan-agents][E10] Tool input must be a JSON object") from exc
    else:
        payload = {}
    if not isinstance(payload, dict):
        raise ValueError("[kantan-agents][E10] Tool input must be a JSON object")
    validate_tool_params(policy, tool_name, payload)


def _run_in_thread(coro_factory: Callable[[], Any]) -> Any:
    def _runner() -> Any:
        return asyncio.run(coro_factory())

    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(_runner).result()
