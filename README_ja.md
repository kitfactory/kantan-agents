# kantan-agents

kantan-agents は OpenAI Agents SDK の薄いラッパで、観測性と評価が "自然に" できる状態を標準で作るライブラリです。

## できること

- Agents SDK tracing API の再エクスポート
- Trace metadata を標準化して自動注入する Agent
- バージョン付き指示のための最小 Prompt モデル
- structured output と `RUBRIC` schema ヘルパ
- Agent インスタンス間の handoff

## クイックスタート

```python
from kantan_agents import Agent

agent = Agent(name="basic-agent", instructions="You are a helpful assistant.")
result = agent.run("Hello")
print(result.final_output)
```

## ドキュメント

- `docs/concept.md`
- `docs/spec.md`
- `docs/architecture.md`
- `docs/plan.md`
- `docs/tutorial_ja.md`
- `docs/usage.md`
