kantan-agents Tutorial (v0.1)

This tutorial is divided into unit documents. Each unit explains the steps, how to implement them, and the code.

Prerequisites

- `OPENAI_API_KEY` is set in the environment
- Use `gpt-5-mini` for testing/verification

Context and policy defaults

- `Agent.run` returns a context dict. Use `context["result"]` to read the SDK result.
- If you need async, use `await Agent.run_async(...)`.
- Context is optional. If you omit it, kantan-agents creates an empty dict.
- If you pass an empty dict, the Agent fills in policy from tool/provider settings.
- `PolicyMode.RECOMMENDED` uses tool/provider policy as the base.
- History is stored in `context["history"]` when enabled.

Units

- Unit 1: Run a minimal Agent (`docs/tutorial/en/unit_01_minimal.md`)
- Unit 2: Use context for templated instructions (`docs/tutorial/en/unit_02_context_template.md`)
- Unit 3: Enable tracing and persist records (`docs/tutorial/en/unit_03_tracing_sqlite.md`)
- Unit 4: Apply policy to tool usage (`docs/tutorial/en/unit_04_policy_tools.md`)
- Unit 5: Use Prompt with versioned instructions (`docs/tutorial/en/unit_05_prompt.md`)
- Unit 6: Use structured output (`docs/tutorial/en/unit_06_structured_output.md`)
- Unit 7: Delegate with handoffs (`docs/tutorial/en/unit_07_handoffs.md`)
- Unit 8: Tool-based evaluation and prompt analysis (`docs/tutorial/en/unit_08_rubric.md`)
- Unit 9: Provide tools via entry points (`docs/tutorial/en/unit_09_entry_points.md`)
- Unit 10: Search traces with kantan-llm (`docs/tutorial/en/unit_10_search_service.md`)

Suggested path

- Start with Unit 1 → Unit 2 to learn context and templates.
- Read Unit 5 to understand Prompt metadata.
- Then go to Unit 3 for tracing and Unit 8 for LLM-as-a-judge.
- For a minimal context template, see `docs/usage.md`.
- Units 4 and 9 are advanced; skip them unless you need policy or entry-point tools.
