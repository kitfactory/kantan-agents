kantan-agents チュートリアル 単元10（v0.1）

タイトル

kantan-llm で Trace を検索する

概要

この単元では Prompt を使って Trace metadata に情報を記録し、Rubric 評価も出力する。Prompt 情報で Trace を検索し、該当 Trace の rubric を取り出して確認する。

ステップ

- Prompt を使って Agent を実行し、Trace metadata に Prompt 情報を記録する。
- output_type=RUBRIC で評価結果を生成する。
- TraceQuery で prompt_name/prompt_version を条件に Trace を検索する。
- 該当する Trace の rubric を取得する。

実現方法

- Prompt の name/version は Trace metadata に保存される。
- TraceQuery(metadata=...) を使うと metadata 条件で検索できる。
- get_spans_by_trace で Trace に紐づく rubric を取得できる。

ソースコード
```python
from kantan_agents import Agent, PolicyMode, Prompt, RUBRIC, get_context_with_policy
from kantan_llm.tracing import SQLiteTracer, TraceQuery

tracer = SQLiteTracer("kantan_agents_traces.sqlite3")

prompt = Prompt(
    name="qa",
    version="v1",
    text="Answer the user briefly.",
    meta={"variant": "A"},
)
agent = Agent(
    name="prompted-agent",
    instructions=prompt,
    output_type=RUBRIC,
)
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = agent.run("Explain tracing in one sentence.", context)
print(context["result"].final_output)

traces = tracer.search_traces(query=TraceQuery(metadata={"prompt_name": "qa", "prompt_version": "v1"}))
for trace in traces:
    spans = tracer.get_spans_by_trace(trace.trace_id)
    rubrics = [span.rubric for span in spans if span.rubric]
    print(trace.trace_id, trace.metadata, rubrics)
```
