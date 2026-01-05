kantan-agents Tutorial (v0.1)

This tutorial is divided into unit documents. Each unit explains the steps, how to implement them, and the code.

Focus

- Switch models with a single string and observe traces early.
- Start small, then enrich traces with Prompt metadata and structured output.

Kantan-first path (recommended)

1. Start with `Agent` + `Prompt` for versioned instructions.
2. Switch models by name without changing Agent code.
3. Enable tracing early (SQLite or your tracer of choice).
4. Add tools via entry points and control them with `tool_rules`.
5. Use structured output (and `RUBRIC`) to evaluate and iterate.

Escape hatches (when you must)

- Async usage is an escape hatch for ASGI; use it only when you must avoid blocking an event loop.
- If you use the Agents SDK directly, keep prompt versions and trace metadata consistent.
- Swap tracing processors to route data to your preferred backend.

Prerequisites

- `OPENAI_API_KEY` is set in the environment
- Use `gpt-5-mini` for testing/verification

Context and tool rules defaults

- `Agent.run` returns a context dict. Use `context["result"]` to read the SDK result.
- If you pass a string model name, kantan-llm resolves it via `get_llm`.
- If you pass AsyncClientBundle/KantanAsyncLLM, kantan-agents injects the AsyncOpenAI client.
- If you need async, use `await Agent.run_async(...)`.
- Context is optional. If you omit it, kantan-agents creates an empty dict.
- If you pass an empty dict, the Agent fills in tool rules from tool/provider defaults.
- `ToolRulesMode.RECOMMENDED` uses tool/provider tool rules as the base.
- History is stored in `context["history"]` when enabled.

Units

- Unit 1: Run a minimal Agent (`docs/tutorial/en/unit_01_minimal.md`)
- Unit 2: Use context for templated instructions (`docs/tutorial/en/unit_02_context_template.md`)
- Unit 3: Enable tracing and persist records (`docs/tutorial/en/unit_03_tracing_sqlite.md`)
- Unit 4: Apply tool rules to tool usage (`docs/tutorial/en/unit_04_tool_rules.md`)
- Unit 5: Use Prompt with versioned instructions (`docs/tutorial/en/unit_05_prompt.md`)
- Unit 6: Use structured output (`docs/tutorial/en/unit_06_structured_output.md`)
- Unit 7: Delegate with handoffs (`docs/tutorial/en/unit_07_handoffs.md`)
- Unit 8: Tool-based evaluation and prompt analysis (`docs/tutorial/en/unit_08_rubric.md`)
- Unit 9: Provide tools via entry points (`docs/tutorial/en/unit_09_entry_points.md`)
- Unit 10: Search traces with kantan-llm (`docs/tutorial/en/unit_10_search_service.md`)

Suggested path

- Start with Unit 1 to get a minimal Agent running.
- Jump to Unit 3 to enable tracing early.
- Read Unit 5 to enrich traces with Prompt metadata.
- Then use Unit 6 for structured output.
- Use Unit 2 when you need templates or context variables.
- Unit 8 is for evaluation; Unit 10 is for trace search.
- Units 4 and 9 are advanced; skip them unless you need tool controls or entry-point tools.
