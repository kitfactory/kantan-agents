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
Prompt の情報は Trace metadata に自動注入される。

```python
from kantan_agents import Agent, Prompt

prompt = Prompt(
    name="qa",
    version="v1",
    text="Answer the user briefly.",
    meta={"variant": "A"},
)

agent = Agent(name="support-agent", instructions=prompt)
context = agent.run("Explain trace metadata in one sentence.")
print(context["result"].final_output)
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

- 固定の Trace メタデータは Agent の `metadata` に設定する。
- 生成結果の structured output や rubric は span に保存される（SQLite の `structured_json` / `rubric_json` を参照）。
- context は省略できる。省略時は空の dict を自動生成する。
- context を渡す場合、空の dict でも Agent が tool/provider の tool_rules 設定を統合する。
- get_context_with_tool_rules(ToolRulesMode.RECOMMENDED) は tool/provider の tool_rules 設定を基準にする。
- history が有効な場合は context["history"] に入力/応答が保存される。
- output_dest を指定すると structured output が context の指定キーに保存される。
- output_dest は既存キーを上書きする。structured output が dict 化できない場合は保存されない。

entry-point 由来の tool_rules 設定

- Agent 初期化時に entry-point provider を読み込み、`list_tools()` と `get_tool_rules()` の結果を統合する。
- 統合順序は「基本 tool_rules 設定 → provider 由来 tool_rules 設定 → 明示 tool_rules 設定」。
- `allow`/`deny` は union、`params` は tool 名ごとに merge。同名キーは上書き。
- 利用側は `get_context_with_tool_rules(ToolRulesMode.RECOMMENDED)` で provider 由来の推奨設定を取り込み、必要に応じて `context["tool_rules"]` を更新する。
- provider 由来の tool 名一覧や設定内容を確認する場合は `list_provider_tools()` と `get_provider_tool_rules()` を使う。

```python
from kantan_agents import Agent, ToolRulesMode, get_context_with_tool_rules

agent = Agent(name="provider-agent", instructions="Use tools when needed.")

context = get_context_with_tool_rules(ToolRulesMode.RECOMMENDED)
context["tool_rules"]["allow"] = ["myorg.search"]
context["tool_rules"]["params"] = {
    "myorg.search": {"query": {"type": "string", "minLength": 1, "maxLength": 200}}
}

context = agent.run("Find docs about tracing.", context)
print(context["result"].final_output)
```

```python
from kantan_agents import get_provider_tool_rules, list_provider_tools

tool_names = list_provider_tools()
tool_rules = get_provider_tool_rules()
print(tool_names)
print(tool_rules["params"])
```

Context の最小テンプレート（渡す場合）

```json
{
  "tool_rules": {},
  "history": [],
  "result": null
}
```

よくある失敗

- context を dict 以外で渡してしまう（対処: {} か get_context_with_tool_rules(...) を渡す）
- tool_rules を上書きして tool が使えなくなる（対処: allow/deny を確認し、必要なら RECOMMENDED を基準に merge する）
- output_dest に dict 以外が入らず保存されない（対処: output_type を設定し、dict で返る structured output を使う）
- Prompt 情報が span ではなく Trace metadata に保存される（対処: Trace metadata を参照する）

エラーIDの1行対処

| Error ID | 対処 |
| --- | --- |
| E1 | Agent に instructions を渡す（文字列または Prompt）。 |
| E2 | Prompt.text を空文字にしない。 |
| E3 | Prompt.name / Prompt.version を空文字にしない。 |
| E4 | tool に name 属性を持たせる（関数なら function_tool 経由を使う）。 |
| E5 | context は dict を渡す（{} または get_context_with_tool_rules(...)）。 |
| E6 | context["history"] は list にする（不要なら history=0）。 |
| E7 | tool provider に list_tools と get_tool_rules を実装する。 |
| E8 | tool_rules の allow/deny を見直して tool を許可する。 |
| E9 | ToolRulesMode の列挙値（ALLOW_ALL / DENY_ALL / RECOMMENDED）を使う。 |
| E10 | tool 入力は JSON オブジェクトで渡す（引数を dict にする）。 |
| E11 | tool_rules.params の type と tool 引数の型を合わせる。 |
| E12 | tool_rules.params の enum に含まれる値を渡す。 |
| E13 | 文字列長が minLength を満たすようにする。 |
| E14 | 文字列長が maxLength を超えないようにする。 |
| E15 | 文字列が pattern に一致するようにする。 |
| E16 | 数値が minimum 以上になるようにする。 |
| E17 | 数値が maximum 以下になるようにする。 |

スニペット集

生成のみ（最小）
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = agent.run("Hello")
print(context["result"].final_output)
```

生成 + 評価（LLM-as-a-judge）
```python
from kantan_agents import Agent, Prompt, RUBRIC

generator_prompt = Prompt(name="A", version="v1", text="Answer briefly.")
generator = Agent(name="generator", instructions=generator_prompt)

context = generator.run("Explain tracing.")
generated = context["result"].final_output

judge_prompt = Prompt(
    name="A-judge",
    version="v1",
    text="Evaluate the answer and output a rubric with score (0-1) and comments.",
)
judge = Agent(name="judge", instructions=judge_prompt, output_type=RUBRIC)
judge_context = judge.run(str(generated))
print(judge_context["result"].final_output)
```

生成 + 保存（output_dest + history）
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
    output_dest="summary_json",
)
context = agent.run("Summarize the release notes.")
print(context["summary_json"]["title"])
print(context["history"])
```
