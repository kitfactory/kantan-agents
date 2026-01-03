kantan-agents チュートリアル 単元2（v0.1）

タイトル

context でテンプレートを使う

概要

この単元では instructions に変数を埋め込む方法を説明する。テンプレートは {{ $ctx.key }} の形式で参照し、run 直前に context に値を入れる。未定義のキーは空文字になるため、必要なものだけ用意すればよい。

ステップ

- instructions に $ctx プレースホルダを入れる。
- context に必要な変数を追加する。
- run に context を渡してレンダリングする。

実現方法

- {{ $ctx.key }} を参照し、context を更新してから run する。
- 既存の context に追記して使い回してもよい。
- history を使う場合は {{ $ctx.history }} を参照する。

ソースコード
```python
from kantan_agents import Agent, PolicyMode, get_context_with_policy

agent = Agent(
    name="templated-agent",
    instructions="Summarize {{ $ctx.topic }} in {{ $ctx.style }}.",
)
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context.update({"topic": "trace metadata", "style": "two sentences"})
context = agent.run("Use concise bullet points.", context)
print(context["result"].final_output)
```

history をテンプレートで使う例
```python
from kantan_agents import Agent, PolicyMode, get_context_with_policy

agent = Agent(
    name="history-agent",
    instructions="Summarize the last exchanges: {{ $ctx.history }}",
)
context = get_context_with_policy(PolicyMode.RECOMMENDED)
context = agent.run("First message", context)
context = agent.run("Second message", context)
print(context["history"])
```
