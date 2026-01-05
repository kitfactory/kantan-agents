# kantan-agents

kantan-agents は OpenAI Agents SDK の薄いラッパで、観測性と評価が "自然に" できる状態を標準で作るライブラリです。

## できること

🚀 主要プロバイダの多様なモデルに対応：モデル名の変更だけで、様々なモデルをAgentとして利用できます。
🔍 記録の自動化：Trace データを自動注入することで、観測と検索の環境が自動的に整います
🧪 Prompt 情報の自動記録：Promptのバージョン情報も自動記録し、結果の管理が容易になります
📦 Context式の出力管理：structured output と history を context に保存して再利用しやすい
🤝 ツール・マルチエージェント対応：tool_rules と handoff により安全に分業できます

## Kantan Stack の位置づけ（概要）

Kantan Stack は「作る → 動かす → 観測/評価 → 改善」を一本道化する設計思想です。  
実行は OpenAI Agents SDK を下回りで使いますが、基本は **kantan-llm / kantan-agents のみ**で統一するのが推奨です。

- kantan-agents：実行時の薄いラッパー（このリポジトリ）
- kantan-llm：モデル解決とトレースの中核
- kantan-tools（予定）：インストールするだけで増えるツール群（スキーマ/権限つき）
- kantan-lab（予定）：トレース/プロンプトの分析と評価、回帰検知

## 推奨ルート（Kantan-first）

1. まず `Agent` + `Prompt` でバージョン付き指示にする  
2. model 名を変えるだけでモデル切り替え  
3. tracing を早めに有効化（SQLite など）  
4. tools は entry-point 経由で追加し、`tool_rules` で制御  
5. structured output / `RUBRIC` で評価し、改善を回す  

## Escape Hatches（必要な場合）

- Agents SDK 直書きは escape hatch 扱いにし、基本は `kantan-llm` / `kantan-agents` を使う  
- async は ASGI のための escape hatch として、必要時のみ使う  
- Agents SDK を直接使う場合も、Prompt 情報と Trace metadata の一貫性を保つ  
- tracing processor は差し替え可能（SQLite/外部基盤など）  

## クイックスタート

```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = agent.run("Hello")
print(context["result"].final_output)
```

model を指定する
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.", model="gpt-5-mini")
context = agent.run("Hello")
print(context["result"].final_output)
```

Tracing（SQLite）
```python
from kantan_agents import Agent, set_trace_processors
from kantan_llm.tracing import SQLiteTracer

tracer = SQLiteTracer("traces.sqlite3")
set_trace_processors([tracer])

agent = Agent(name="trace-agent", instructions="短く答えてください。")
context = agent.run("なぜ tracing は便利？")
print(context["result"].final_output)
```

AsyncClientBundle を使う（escape hatch）
```python
from kantan_llm import get_async_llm_client
from kantan_agents import Agent

bundle = get_async_llm_client("gpt-5-mini")
agent = Agent(name="basic-agent", instructions="You are a helpful assistant.", model=bundle)
context = agent.run("Hello")
print(context["result"].final_output)
```

非同期の使い方（escape hatch）
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = await agent.run_async("Hello")
print(context["result"].final_output)
```

## ミニチュートリアル（やさしい散歩）

`context` は Agent が背負うリュックだと思ってください。実行のたびに `context["result"]`
へ結果が入ります。さらに、構造化出力や履歴なども同じリュックに入れられます。

### Step 1: Prompt に名札をつける（Prompt + metadata）
```python
from kantan_agents import Agent, Prompt

prompt = Prompt(
    name="qa",
    version="v1",
    text="1文で短く答えてください。",
    meta={"tone": "friendly"},
)

agent = Agent(name="support-agent", instructions=prompt)
context = agent.run("Trace metadata って何？")
print(context["result"].final_output)
```
Prompt の名前やバージョンが trace metadata に残るので、後から追いやすくなります。

### Step 2: モデルをさっと切り替える
```python
from kantan_agents import Agent

agent = Agent(name="switcher", instructions="1文で答えてください。", model="gpt-5-mini")
context = agent.run("モデル切り替えが簡単だと何が嬉しい？")
print(context["result"].final_output)
```

### Step 3: Tracing をオンにする（SQLite）
```python
from kantan_agents import set_trace_processors
from kantan_llm.tracing import SQLiteTracer

tracer = SQLiteTracer("traces.sqlite3")
set_trace_processors([tracer])
```
SQLite でサクッと確認できます:
```python
import sqlite3

conn = sqlite3.connect("traces.sqlite3")
conn.row_factory = sqlite3.Row
row = conn.execute(
    "SELECT id, metadata_json FROM traces ORDER BY id DESC LIMIT 1"
).fetchone()
print(dict(row))
```

### Step 4: 構造化出力でキレイに受け取る
```python
from pydantic import BaseModel
from kantan_agents import Agent

class Summary(BaseModel):
    title: str
    bullets: list[str]

agent = Agent(
    name="summarizer",
    instructions="タイトルと箇条書き2点で要約してください。",
    output_type=Summary,
    output_dest="summary_json",
)

context = agent.run("なぜ tracing はチームに効くの？")
print(context["summary_json"]["title"])
```

### Step 5: ASGI で async（client 注入）
`get_async_llm_client()` で AsyncOpenAI client を Agents SDK に注入できます:
```python
from kantan_llm import get_async_llm_client
from kantan_agents import Agent

bundle = get_async_llm_client("gpt-5-mini")
agent = Agent(name="async-agent", instructions="Hiと挨拶して。", model=bundle)
context = await agent.run_async("Hello")
print(context["result"].final_output)
```

## ドキュメント

- `docs/concept.md`
- `docs/spec.md`
- `docs/architecture.md`
- `docs/plan.md`
- `docs/tutorial_ja.md`
- `docs/usage.md`
