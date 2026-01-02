kantan-agents 最小利用ガイド（v0.1）

このドキュメントは、tracing 設定 → Agent 作成 → run → SQLite 検索の最小例を示す。

1. tracing 設定（SQLite）

kantan-llm の SQLiteTracer を tracing processor として登録する。

```python
from kantan_llm.tracing import SQLiteTracer
from kantan_agents import set_trace_processors

tracer = SQLiteTracer("kantan_agents_traces.sqlite3")
set_trace_processors([tracer])
```

2. Agent 作成と run

Prompt を使い、Trace metadata に prompt/agent/run の標準キーが残るようにする。

```python
from kantan_agents import Agent, Prompt

prompt = Prompt(
    name="qa",
    version="v1",
    text="Answer the user briefly.",
    meta={"variant": "A"},
)

agent = Agent(name="support-agent", instructions=prompt)
result = agent.run(
    "Explain trace metadata in one sentence.",
    trace_metadata={"session_id": "sess-001"},
)
print(result.final_output)
```

3. SQLite 検索

SQLite に保存された trace/span を検索する。

```python
import sqlite3

conn = sqlite3.connect("kantan_agents_traces.sqlite3")
conn.row_factory = sqlite3.Row

trace = conn.execute(
    "SELECT id, metadata_json FROM traces ORDER BY id DESC LIMIT 1"
).fetchone()
print(dict(trace))

spans = conn.execute(
    "SELECT span_type, name, output_kind, rubric_json FROM spans WHERE trace_id = ? ORDER BY ingest_seq",
    (trace["id"],),
).fetchall()
print([dict(row) for row in spans])
```

補足

- `trace_metadata` に `session_id` などを渡すと、後続分析でフィルタしやすくなる。
- 生成結果の structured output や rubric は span に保存される（SQLite の `structured_json` / `rubric_json` を参照）。
