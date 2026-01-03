kantan-agents Tutorial (v0.1)

This tutorial is divided into unit documents. Each unit explains the steps, how to implement them, and the code.

Prerequisites

- `OPENAI_API_KEY` is set in the environment
- Use `gpt-5-mini` for testing/verification

Context and policy defaults

- `Agent.run` returns a context dict. Use `context["result"]` to read the SDK result.
- Pass a context dict. Use `get_context_with_policy(PolicyMode.RECOMMENDED)` as a baseline.
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
