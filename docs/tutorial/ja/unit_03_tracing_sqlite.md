kantan-agents チュートリアル 単元3（v0.1）

タイトル

tracing を有効化して記録を残す

概要

この単元では Trace を SQLite に保存する。トレーサはプロセス単位で一度登録し、複数の run で再利用する。後から span を検索して内容を確認できる。

ステップ

- SQLiteTracer を作成する。
- set_trace_processors で登録する。
- Agent を実行して Trace を書き込む。

実現方法

- SQLiteTracer と set_trace_processors を使う。
- トレーサは同じインスタンスを使い回す。

ソースコード
```python
from kantan_llm.tracing import SQLiteTracer
from kantan_agents import Agent, PolicyMode, get_context_with_policy, set_trace_processors

tracer = SQLiteTracer("kantan_agents_traces.sqlite3")
set_trace_processors([tracer])

agent = Agent(name="trace-agent", instructions="Answer briefly.")
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = agent.run("Explain trace metadata in one sentence.", context)
print(context["result"].final_output)
```
