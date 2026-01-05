# kantan-agents

kantan-agents は OpenAI Agents SDK の薄いラッパで、観測性と評価が "自然に" できる状態を標準で作るライブラリです。

## できること

- Agents SDK tracing API の再エクスポート
- Trace metadata を標準化して自動注入する Agent
- バージョン付き指示のための最小 Prompt モデル
- Prompt 利用時に Trace metadata へ Prompt 情報を自動注入する
- 入力/応答の履歴を context の history に保存する
- structured output を output_dest 指定で context に保存できる
- structured output と `RUBRIC` schema ヘルパ
- Agent インスタンス間の handoff
- entry-point から tool と tool_rules 設定を収集する
- provider 由来の tool と tool_rules 設定を確認するヘルパを提供する
- model 名を文字列で渡すと kantan-llm の get_llm で解決する
- AsyncClientBundle/KantanAsyncLLM を渡すと AsyncOpenAI client を注入できる

## クイックスタート

```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = agent.run("Hello")
print(context["result"].final_output)
```

非同期の使い方
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
context = await agent.run_async("Hello")
print(context["result"].final_output)
```

model を指定する
```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.", model="gpt-5-mini")
context = agent.run("Hello")
print(context["result"].final_output)
```

AsyncClientBundle を使う
```python
from kantan_llm import get_async_llm_client
from kantan_agents import Agent

bundle = get_async_llm_client("gpt-5-mini")
agent = Agent(name="basic-agent", instructions="You are a helpful assistant.", model=bundle)
context = agent.run("Hello")
print(context["result"].final_output)
```

## ドキュメント

- `docs/concept.md`
- `docs/spec.md`
- `docs/architecture.md`
- `docs/plan.md`
- `docs/tutorial_ja.md`
- `docs/usage.md`
