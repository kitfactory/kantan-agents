kantan-agents チュートリアル（v0.1）

このチュートリアルは段階的に単元を分け、各単元を「利用ケース → 実現方法 → ソースコード」の順で説明する。
最後はツールを使ったエージェントで評価を含めてプロンプトの分析を行う。

前提

- OPENAI_API_KEY が環境変数に設定済み
- テスト/動作確認では gpt-5-mini を使用

単元1: 最小構成で Agent を動かす

利用ケース:
シンプルな質問応答を行い、Agent が動作することを確認する。

実現方法:
Agent を作成して run を呼び出す。結果は Agents SDK と同じ返値が返る。

ソースコード:
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
result = agent.run("Hello")
print(result.final_output)
```

単元2: tracing を有効化して記録を残す

利用ケース:
Trace を SQLite に保存し、後で検索できるようにする。

実現方法:
kantan-llm の SQLiteTracer を登録してから Agent を実行する。

ソースコード:
```python
from kantan_llm.tracing import SQLiteTracer
from kantan_agents import Agent, set_trace_processors

tracer = SQLiteTracer("kantan_agents_traces.sqlite3")
set_trace_processors([tracer])

agent = Agent(name="trace-agent", instructions="Answer briefly.")
result = agent.run("Explain trace metadata in one sentence.")
print(result.final_output)
```

単元3: Prompt 型でバージョン付き指示を使う

利用ケース:
プロンプトの name/version を Trace に残し、後で分析できる状態にする。

実現方法:
Prompt を作成して Agent に渡す。run 実行時に標準メタデータが自動注入される。

ソースコード:
```python
from kantan_agents import Agent, Prompt

prompt = Prompt(
    name="qa",
    version="v1",
    text="Answer the user briefly.",
    meta={"variant": "A"},
)

agent = Agent(name="prompted-agent", instructions=prompt)
result = agent.run(
    "Explain tracing in one sentence.",
    trace_metadata={"session_id": "sess-001"},
)
print(result.final_output)
```

単元4: structured output を使う

利用ケース:
構造化出力で結果を取得し、分析しやすい出力形式を作る。

実現方法:
output_type に Pydantic モデルを指定する。

ソースコード:
```python
from pydantic import BaseModel
from kantan_agents import Agent

class Summary(BaseModel):
    title: str
    bullets: list[str]

agent = Agent(
    name="structured-agent",
    instructions="Summarize the input.",
    output_type=Summary,
)
result = agent.run("Summarize the release notes.")
print(result.final_output)
```

単元5: handoffs でサブエージェントへ委譲する

利用ケース:
専門エージェントに仕事を分担し、会話を引き継ぐ。

実現方法:
handoffs に別 Agent を渡して委譲できる構成にする。

ソースコード:
```python
from kantan_agents import Agent

booking_agent = Agent(name="booking", instructions="Handle booking tasks.")
refund_agent = Agent(name="refund", instructions="Handle refund tasks.")

manager = Agent(
    name="manager",
    instructions="Route tasks to specialists.",
    handoffs=[booking_agent, refund_agent],
)
result = manager.run("I need a refund for last week's order.")
print(result.final_output)
```

単元6: ツールを使った評価とプロンプト分析

利用ケース:
ツールの実行結果と評価（rubric）が Trace に残り、kantan-lab でプロンプト改善の材料にする。

実現方法:
tools に関数を渡し、output_type に RUBRIC を指定する。

ソースコード:
```python
from kantan_agents import Agent, RUBRIC


def word_count(text: str) -> int:
    return len(text.split())

agent = Agent(
    name="evaluator",
    instructions="Use word_count and then output a rubric with score and comments.",
    tools=[word_count],
    output_type=RUBRIC,
)
result = agent.run("Assess this sentence: 'Tracing enables analysis.'")
print(result.final_output)
```

kantan-llm 検索サービスの利用例

- TraceSearchService を使って trace/span を検索し、評価結果を分析する。

```python
from kantan_llm.tracing import SQLiteTracer, SpanQuery

tracer = SQLiteTracer("kantan_agents_traces.sqlite3")
spans = tracer.search_spans(query=SpanQuery(limit=10))

for span in spans:
    print(span.span_type, span.output_kind, span.structured, span.rubric)
```
